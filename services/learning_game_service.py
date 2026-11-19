"""Transactional, HTTP-free progression rules for the Game MVP."""

from __future__ import annotations

import math
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Mapping

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models_game import (
    GameBookEntry,
    GameDialogueState,
    GameLessonAttempt,
    GameProgress,
    GameTaskAttempt,
    GameTaskResult,
)
from services import game_rewards_service
from services.game_scoring import score_ddo
from services.game_content.achievements import STARK_WARNING_LINES
from services.game_content.catalog import (
    CATALOG,
    CHURCHILL_CATALOG,
    MAYAKOVSKY_CATALOG,
    PYTHAGORAS_CATALOG,
    SHELDON_CATALOG,
    ContentCatalog,
)
from services.game_content.onboarding import (
    DDO_NODE_CODE,
    MAP_LOCATIONS,
    ONBOARDING_NODES,
    map_locations_after_klimov,
)
from services.game_content.shop import ASTRA_HINT_FALLBACK, ATTEMPT_STABILIZER_HINT


INITIAL_NODE_CODE = "ПР-01"
POST_DDO_NODE_CODE = "ПР-05"
KLIMOV_PROFILES = frozenset(("chp", "cht", "chch", "chz", "chkh"))
KLIMOV_TIE_PRIORITY = ("chch", "cht", "chp", "chz", "chkh")
GROWTH_CHARACTERISTICS = (
    ("chp", "Ч-П", "Природа"),
    ("cht", "Ч-Т", "Техника"),
    ("chch", "Ч-Ч", "Люди"),
    ("chz", "Ч-З", "Знаки"),
    ("chkh", "Ч-Х", "Образ"),
)
_SOLUTION_HINT_LEVEL = 5
_ONBOARDING_NEXT = {
    node.code: ONBOARDING_NODES[index + 1].code
    for index, node in enumerate(ONBOARDING_NODES[:-1])
}
_ONBOARDING_NEXT["ПР-07"] = "stage_hub"
_PYTHAGORAS_PROFILE = "chz"
_MAYAKOVSKY_PROFILE = "chkh"
_SHELDON_PROFILE = "chp"
_CHURCHILL_PROFILE = "chch"


from services.game_errors import (
    ContentNotFoundError,
    InvalidAnswerError,
    InvalidStateError,
    LockedContentError,
    GameGameError,
)


@dataclass(frozen=True)
class GameState:
    current_node_code: str | None
    ddo_profile: str | None
    map_locations: dict[str, dict[str, Any]]
    available_lessons: tuple[str, ...]
    stage_statuses: dict[int, str]
    completed_lesson_codes: tuple[str, ...]
    unlocked_book_cards: tuple[str, ...]
    task_statuses: dict[str, str]
    dialogue_states: dict[str, dict[str, Any]]
    task_progress: dict[str, dict[str, Any]]
    ddo_scores: dict[str, int] | None
    ddo_dominant_codes: tuple[str, ...]
    growth_hall: dict[str, Any]
    sircoins: int
    shop: dict[str, Any]
    lesson_results: dict[str, dict[str, Any]]
    achievement_progress: dict[str, dict[str, Any]]
    first_click_seen: dict[str, bool]

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["available_lessons"] = list(self.available_lessons)
        payload["completed_lesson_codes"] = list(self.completed_lesson_codes)
        payload["unlocked_book_cards"] = list(self.unlocked_book_cards)
        payload["ddo_dominant_codes"] = list(self.ddo_dominant_codes)
        return payload


@dataclass(frozen=True)
class SceneTransition:
    current_node_code: str
    unlocked_book_card_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TaskSubmission:
    correct: bool
    hint: str | None
    help_available: bool
    status: str | None = None
    current_node_code: str | None = None
    lesson_hints_used: int = 0
    stark_warning: dict[str, Any] | None = None
    solution: str | None = None
    consequence: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StarkHelp:
    status: str
    solution: str
    consequence: str
    current_node_code: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _astra_hint_for_task(task: Any) -> str:
    if task.hints:
        return f"АСТРА: «{task.hints[0].text}»"
    return ASTRA_HINT_FALLBACK


def catalog_for_profile(profile: str | None) -> ContentCatalog:
    if profile == _SHELDON_PROFILE:
        return SHELDON_CATALOG
    if profile == _CHURCHILL_PROFILE:
        return CHURCHILL_CATALOG
    if profile == _PYTHAGORAS_PROFILE:
        return PYTHAGORAS_CATALOG
    if profile == _MAYAKOVSKY_PROFILE:
        return MAYAKOVSKY_CATALOG
    return CATALOG


def catalog_for_task_code(task_code: str) -> ContentCatalog:
    if task_code in SHELDON_CATALOG.tasks:
        return SHELDON_CATALOG
    if task_code in CHURCHILL_CATALOG.tasks:
        return CHURCHILL_CATALOG
    if task_code in PYTHAGORAS_CATALOG.tasks:
        return PYTHAGORAS_CATALOG
    if task_code in MAYAKOVSKY_CATALOG.tasks:
        return MAYAKOVSKY_CATALOG
    return CATALOG


def _catalog_for_progress(progress: GameProgress) -> ContentCatalog:
    return catalog_for_profile(progress.ddo_profile)


def _learning_node_for_task(task: Any, catalog: ContentCatalog) -> Any:
    learning_nodes = [
        node for node in catalog.dialogue_nodes.values()
        if getattr(node, "next_code", None) == task.code
    ]
    if not learning_nodes:
        raise InvalidStateError("Task has no mini-learning scene")
    return learning_nodes[0]


async def _get_or_create_progress(
    db: AsyncSession,
    student_id: uuid.UUID,
) -> GameProgress:
    # All service operations hold this student's lock until the caller commits.
    # ON CONFLICT also serializes concurrent first requests without a PK error.
    await db.flush()
    await db.execute(
        insert(GameProgress)
        .values(student_id=student_id, current_node_code=INITIAL_NODE_CODE,
                completed_lesson_codes=[])
        .on_conflict_do_nothing(index_elements=[GameProgress.student_id])
    )
    return (await db.execute(
        select(GameProgress)
        .where(GameProgress.student_id == student_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )).scalar_one()


async def _task_statuses(
    db: AsyncSession,
    student_id: uuid.UUID,
) -> dict[str, str]:
    rows = (
        await db.execute(
            select(GameTaskResult).where(
                GameTaskResult.student_id == student_id
            )
        )
    ).scalars()
    return {row.task_code: row.status for row in rows}


async def _unlocked_card_ids(
    db: AsyncSession,
    student_id: uuid.UUID,
) -> tuple[str, ...]:
    return tuple(
        (
            await db.execute(
                select(GameBookEntry.book_card_id)
                .where(GameBookEntry.student_id == student_id)
                .order_by(GameBookEntry.unlocked_at, GameBookEntry.book_card_id)
            )
        ).scalars()
    )


def _stage_statuses(progress: GameProgress, catalog: ContentCatalog) -> dict[int, str]:
    if progress.ddo_profile is None:
        return {1: "locked", 2: "locked", 3: "soon", 4: "soon"}
    completed = progress.completed_lesson_codes or []
    return {
        1: catalog.stage_status(1, completed_lessons=completed),
        2: catalog.stage_status(2, completed_lessons=completed),
        3: catalog.stage_status(3, completed_lessons=completed),
        4: catalog.stage_status(4, completed_lessons=completed),
    }


def _map_locations(profile: str | None) -> dict[str, dict[str, Any]]:
    if profile is None:
        return {code: dict(location) for code, location in MAP_LOCATIONS.items()}
    return map_locations_after_klimov(profile)


def _growth_hall(scores: dict[str, int] | None) -> dict[str, Any]:
    characteristics = []
    if scores:
        characteristics = [
            {
                "profile": profile,
                "code": code,
                "title": title,
                "score": scores[profile],
                "max_score": 8,
                "source": "klimov_ddo",
            }
            for profile, code, title in GROWTH_CHARACTERISTICS
            if profile in scores
        ]
    return {
        "is_enabled": False,
        "status": "future",
        "characteristics": characteristics,
    }


async def get_state(db: AsyncSession, student_id: uuid.UUID) -> GameState:
    """Return the student's public state, creating initial progress lazily."""
    progress = await _get_or_create_progress(db, student_id)
    catalog = _catalog_for_progress(progress)
    completed = tuple(progress.completed_lesson_codes or [])
    lessons = catalog.available_lessons(completed) if progress.ddo_profile else ()
    dialogues = (await db.execute(select(GameDialogueState).where(
        GameDialogueState.student_id == student_id
    ))).scalars().all()
    dialogue_states = {
        row.node_code: {
            "viewed_question_codes": list(row.viewed_question_codes or []),
            "selected_choice_code": row.selected_choice_code,
            "action_state": row.action_state,
            "completed": row.completed_at is not None,
        }
        for row in dialogues
    }
    current = catalog.dialogue_nodes.get(progress.current_node_code)
    if current is not None and current.mode == "action":
        dialogue_states.setdefault(current.code, {
            "viewed_question_codes": [], "selected_choice_code": None,
            "action_state": current.initial_state, "completed": False,
        })
    statuses = await _task_statuses(db, student_id)
    attempts = (await db.execute(select(GameTaskAttempt).where(
        GameTaskAttempt.student_id == student_id,
        GameTaskAttempt.is_correct.is_(False),
    ).order_by(GameTaskAttempt.task_code, GameTaskAttempt.error_number))).scalars()
    task_progress = {
        task.code: {"wrong_attempt_count": 0, "issued_hints": [], "help_available": False}
        for task in catalog.tasks.values() if task.lesson_code in lessons
    }
    for attempt in attempts:
        entry = task_progress.get(attempt.task_code)
        if entry is None:
            continue
        entry["wrong_attempt_count"] += 1
        task = catalog.task(attempt.task_code)
        for hint in task.hints:
            if hint.level < _SOLUTION_HINT_LEVEL and attempt.hint_code == f"{task.code}-H{hint.level}":
                issued = {"code": attempt.hint_code, "level": hint.level, "text": hint.text}
                if issued not in entry["issued_hints"]:
                    entry["issued_hints"].append(issued)
    for task_code, entry in task_progress.items():
        entry["help_available"] = entry["wrong_attempt_count"] >= 5 and task_code not in statuses
    return GameState(
        current_node_code=progress.current_node_code,
        ddo_profile=progress.ddo_profile,
        map_locations=_map_locations(progress.ddo_profile),
        available_lessons=lessons,
        stage_statuses=_stage_statuses(progress, catalog),
        completed_lesson_codes=completed,
        unlocked_book_cards=await _unlocked_card_ids(db, student_id),
        task_statuses=statuses,
        dialogue_states=dialogue_states,
        task_progress=task_progress,
        ddo_scores=progress.ddo_scores,
        ddo_dominant_codes=tuple(progress.ddo_dominant_codes or []),
        growth_hall=_growth_hall(progress.ddo_scores),
        sircoins=await game_rewards_service.wallet_balance(db, student_id),
        shop=await game_rewards_service.shop_state(
            db,
            student_id,
            current_task_code=(
                progress.current_node_code
                if progress.current_node_code in catalog.tasks
                else None
            ),
        ),
        lesson_results=await game_rewards_service.lesson_results_state(db, student_id),
        achievement_progress=await game_rewards_service.achievement_progress_state(db, student_id),
        first_click_seen=await game_rewards_service.first_click_state(db, student_id),
    )


def _get_node(node_code: str, catalog: ContentCatalog) -> Any:
    try:
        return catalog.dialogue_nodes[node_code]
    except KeyError as exc:
        raise ContentNotFoundError(f"Unknown dialogue node: {node_code}") from exc


def _get_lesson(lesson_code: str, catalog: ContentCatalog) -> Any:
    try:
        return catalog.lesson(lesson_code)
    except KeyError as exc:
        raise ContentNotFoundError(f"Unknown lesson: {lesson_code}") from exc


def _get_task(task_code: str, catalog: ContentCatalog) -> Any:
    try:
        return catalog.task(task_code)
    except KeyError as exc:
        raise ContentNotFoundError(f"Unknown task: {task_code}") from exc


def _require_lesson_access(progress: GameProgress, lesson: Any, catalog: ContentCatalog) -> None:
    if progress.ddo_profile is None:
        raise LockedContentError("Klimov DDO must be completed before Stark lessons")
    completed = set(progress.completed_lesson_codes or [])
    if catalog.stage_status(lesson.stage, completed_lessons=completed) != "available":
        raise LockedContentError(f"Stage {lesson.stage} is not available")
    if not set(lesson.prerequisite_codes).issubset(completed):
        raise LockedContentError(f"Lesson prerequisites are not complete: {lesson.code}")


async def _require_node_access(
    db: AsyncSession,
    progress: GameProgress,
    node: Any,
    catalog: ContentCatalog,
) -> None:
    if node.code in {"ПР-05", "ПР-06", "ПР-07"} and progress.ddo_profile is None:
        raise LockedContentError("Klimov DDO must be completed first")

    lesson_code = getattr(node, "lesson_code", "")
    if lesson_code:
        _require_lesson_access(progress, _get_lesson(lesson_code, catalog), catalog)

    completed_lessons = set(progress.completed_lesson_codes or [])
    required_lessons = set(getattr(node, "required_lesson_codes", ()))
    if not required_lessons.issubset(completed_lessons):
        raise LockedContentError(f"Dialogue prerequisites are not complete: {node.code}")

    required_tasks = set(getattr(node, "required_task_codes", ()))
    if required_tasks:
        statuses = await _task_statuses(db, progress.student_id)
        if not required_tasks.issubset(statuses):
            raise LockedContentError(f"Required tasks are not complete: {node.code}")


async def _unlock_book_card(
    db: AsyncSession,
    student_id: uuid.UUID,
    book_card_id: str,
) -> bool:
    if not book_card_id:
        return False
    existing = await db.get(GameBookEntry, (student_id, book_card_id))
    if existing is not None:
        return False
    db.add(GameBookEntry(student_id=student_id, book_card_id=book_card_id))
    await db.flush()
    return True


def _is_replay(progress: GameProgress, lesson_code: str) -> bool:
    return lesson_code in (progress.completed_lesson_codes or [])


async def _abandon_open_attempt(db: AsyncSession, student_id: uuid.UUID, lesson_code: str) -> None:
    open_attempt = await _get_open_lesson_attempt(db, student_id, lesson_code)
    if open_attempt is not None:
        open_attempt.status = "abandoned"


async def _start_lesson_attempt(
    db: AsyncSession, student_id: uuid.UUID, lesson_code: str
) -> GameLessonAttempt:
    await _abandon_open_attempt(db, student_id, lesson_code)
    attempt = GameLessonAttempt(student_id=student_id, lesson_code=lesson_code, status="in_progress")
    db.add(attempt)
    await db.flush()
    return attempt


async def _get_open_lesson_attempt(
    db: AsyncSession, student_id: uuid.UUID, lesson_code: str
) -> GameLessonAttempt | None:
    return (await db.execute(
        select(GameLessonAttempt).where(
            GameLessonAttempt.student_id == student_id,
            GameLessonAttempt.lesson_code == lesson_code,
            GameLessonAttempt.status == "in_progress",
        )
    )).scalar_one_or_none()


async def _current_lesson_attempt(
    db: AsyncSession, student_id: uuid.UUID, lesson_code: str
) -> GameLessonAttempt:
    attempt = await _get_open_lesson_attempt(db, student_id, lesson_code)
    if attempt is None:
        raise InvalidStateError(f"No active attempt for lesson: {lesson_code}")
    return attempt


async def advance_scene(
    db: AsyncSession,
    student_id: uuid.UUID,
    node_code: str,
) -> SceneTransition:
    """Follow the current node's single permitted edge, never a client jump."""
    progress = await _get_or_create_progress(db, student_id)
    catalog = _catalog_for_progress(progress)
    if node_code not in catalog.dialogue_nodes and node_code not in catalog.tasks and node_code != "stage_hub":
        raise ContentNotFoundError(f"Unknown scene: {node_code}")
    current = progress.current_node_code
    if current == "stage_hub":
        if node_code not in {"Э2-ВХОД-В", "Э2-ФИНАЛ"}:
            raise InvalidStateError("Enter a lesson from the stage hub")
    else:
        if current in catalog.tasks:
            raise InvalidStateError("Complete the current task before continuing")
        source = _get_node(current, catalog)
        if current == DDO_NODE_CODE:
            raise InvalidStateError("Submit Klimov DDO before continuing")
        state = await _dialogue_state(db, student_id, current)
        if source.mode == "choice" and state.selected_choice_code is None:
            raise InvalidStateError("Select a dialogue choice before continuing")
        if source.mode == "action" and state.action_state != source.completed_state:
            raise InvalidStateError("Complete the interface actions before continuing")
        expected = getattr(source, "next_code", "") or _ONBOARDING_NEXT.get(current)
        if source.mode == "choice":
            choice = next(item for item in source.choices if item["code"] == state.selected_choice_code)
            expected = choice.get("next_code", expected)
        if node_code != expected:
            raise InvalidStateError(f"Scene is not the next node from {current}")
        state.completed_at = datetime.now(timezone.utc)

    card_id = ""
    if node_code in catalog.tasks:
        task = _get_task(node_code, catalog)
        await _require_task_learning(db, progress, task, catalog, require_current=False)
        existing_result = await db.get(GameTaskResult, (student_id, task.code))
        if existing_result is not None and not _is_replay(progress, task.lesson_code):
            node_code = task.next_node_code
    if node_code in catalog.dialogue_nodes:
        node = _get_node(node_code, catalog)
        await _require_node_access(db, progress, node, catalog)
        card_id = getattr(node, "book_card_id", "")
    progress.current_node_code = node_code
    await _unlock_book_card(db, student_id, card_id)
    await db.flush()
    return SceneTransition(
        current_node_code=node_code,
        unlocked_book_card_id=card_id or None,
    )


async def _dialogue_state(
    db: AsyncSession,
    student_id: uuid.UUID,
    node_code: str,
) -> GameDialogueState:
    state = await db.get(GameDialogueState, (student_id, node_code))
    if state is None:
        state = GameDialogueState(
            student_id=student_id,
            node_code=node_code,
            viewed_question_codes=[],
        )
        db.add(state)
        await db.flush()
    return state


async def view_question(
    db: AsyncSession,
    student_id: uuid.UUID,
    node_code: str,
    question_code: str,
) -> dict[str, str]:
    progress = await _get_or_create_progress(db, student_id)
    catalog = _catalog_for_progress(progress)
    node = _get_node(node_code, catalog)
    await _require_node_access(db, progress, node, catalog)
    _require_current_node(progress, node_code)
    if node.mode != "questions":
        raise InvalidStateError(f"Dialogue node does not contain optional questions: {node_code}")
    question = next(
        (dict(item) for item in node.questions if item.get("code") == question_code),
        None,
    )
    if question is None:
        raise ContentNotFoundError(
            f"Unknown question {question_code} for dialogue node {node_code}"
        )
    state = await _dialogue_state(db, student_id, node_code)
    viewed = list(state.viewed_question_codes or [])
    if question_code not in viewed:
        state.viewed_question_codes = [*viewed, question_code]
    progress.current_node_code = node_code
    await db.flush()
    return question


async def select_option(
    db: AsyncSession,
    student_id: uuid.UUID,
    node_code: str,
    choice_code: str,
) -> dict[str, str]:
    progress = await _get_or_create_progress(db, student_id)
    catalog = _catalog_for_progress(progress)
    node = _get_node(node_code, catalog)
    await _require_node_access(db, progress, node, catalog)
    _require_current_node(progress, node_code)
    if node.mode != "choice":
        raise InvalidStateError(f"Dialogue node does not contain a choice: {node_code}")
    choice = next(
        (dict(item) for item in node.choices if item.get("code") == choice_code),
        None,
    )
    if choice is None:
        raise ContentNotFoundError(
            f"Unknown choice {choice_code} for dialogue node {node_code}"
        )
    state = await _dialogue_state(db, student_id, node_code)
    if state.selected_choice_code is not None:
        raise InvalidStateError(f"A choice was already selected for {node_code}")
    state.selected_choice_code = choice_code
    state.completed_at = datetime.now(timezone.utc)
    progress.current_node_code = node_code
    await db.flush()
    if node_code == INITIAL_NODE_CODE:
        await game_rewards_service.sync_achievements(db, student_id)
    return choice


def _require_current_node(progress: GameProgress, node_code: str) -> None:
    if progress.current_node_code != node_code:
        raise InvalidStateError(f"Current scene is not {node_code}")


async def perform_action(db: AsyncSession, student_id: uuid.UUID, node_code: str,
                         action_id: str) -> dict[str, Any]:
    progress = await _get_or_create_progress(db, student_id)
    catalog = _catalog_for_progress(progress)
    node = _get_node(node_code, catalog)
    _require_current_node(progress, node_code)
    if node.mode != "action":
        raise InvalidStateError("Current scene has no interface actions")
    if action_id not in node.action_ids:
        raise ContentNotFoundError(f"Unknown action: {action_id}")
    state = await _dialogue_state(db, student_id, node_code)
    try:
        state.action_state = node.apply_action(state.action_state or node.initial_state, action_id)
    except ValueError as exc:
        raise InvalidStateError(str(exc)) from exc
    complete = node.is_complete(state.action_state)
    if complete:
        state.completed_at = datetime.now(timezone.utc)
    await db.flush()
    return {"current_node_code": node_code, "action_state": state.action_state,
            "completed": complete}


def _profile_from_submission(answers_or_profile: Any) -> tuple[str, dict[str, int] | None, list[str]]:
    scores = None
    dominant = []
    if isinstance(answers_or_profile, str):
        profile = answers_or_profile
    elif isinstance(answers_or_profile, Mapping):
        if set(answers_or_profile) == {"profile"}:
            profile = answers_or_profile["profile"]
        else:
            expected_questions = {str(number) for number in range(1, 21)}
            if set(answers_or_profile) != expected_questions or not all(
                answer in {"a", "b"} for answer in answers_or_profile.values()
            ):
                raise InvalidAnswerError("Klimov DDO requires answers a/b for questions 1-20")
            chp, cht, chch, chz, chkh, _ = score_ddo(dict(answers_or_profile))
            scores = {"chp": chp, "cht": cht, "chch": chch, "chz": chz, "chkh": chkh}
            highest = max(scores.values())
            dominant = [code for code in KLIMOV_TIE_PRIORITY if scores[code] == highest]
            profile = dominant[0]
    else:
        raise InvalidAnswerError("Klimov submission must be a profile or answer mapping")

    if profile not in KLIMOV_PROFILES:
        raise InvalidAnswerError(f"Unknown Klimov profile: {profile}")
    return profile, scores, dominant


async def submit_klimov(
    db: AsyncSession,
    student_id: uuid.UUID,
    answers_or_profile: Any,
) -> GameState:
    progress = await _get_or_create_progress(db, student_id)
    if progress.ddo_profile is not None:
        raise InvalidStateError("Klimov DDO was already submitted")
    _require_current_node(progress, DDO_NODE_CODE)
    progress.ddo_profile, progress.ddo_scores, progress.ddo_dominant_codes = _profile_from_submission(answers_or_profile)
    state = await _dialogue_state(db, student_id, DDO_NODE_CODE)
    state.completed_at = datetime.now(timezone.utc)
    progress.current_node_code = POST_DDO_NODE_CODE
    await db.flush()
    return await get_state(db, student_id)


async def enter_lesson(
    db: AsyncSession,
    student_id: uuid.UUID,
    lesson_code: str,
) -> SceneTransition:
    progress = await _get_or_create_progress(db, student_id)
    catalog = _catalog_for_progress(progress)
    lesson = _get_lesson(lesson_code, catalog)
    _require_lesson_access(progress, lesson, catalog)
    handoff = await db.get(GameDialogueState, (student_id, "ПР-07"))
    if handoff is None or handoff.selected_choice_code is None:
        raise InvalidStateError("Complete the onboarding handoff before entering a lesson")
    if not lesson.dialogue_node_codes:
        raise InvalidStateError(f"Lesson has no entry scene: {lesson_code}")
    entry_code = lesson.dialogue_node_codes[0]
    progress.current_node_code = entry_code
    await _start_lesson_attempt(db, student_id, lesson_code)
    await db.flush()
    return SceneTransition(current_node_code=entry_code)


def _json_answer(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_answer(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_answer(item) for item in value]
    return value


def _numeric_equal(actual: Any, expected: Any) -> bool:
    if isinstance(actual, bool) or isinstance(expected, bool):
        return False
    if not isinstance(actual, (int, float)) or not isinstance(expected, (int, float)):
        return False
    if not math.isfinite(float(actual)) or not math.isfinite(float(expected)):
        return False
    if isinstance(expected, int):
        return float(actual) == float(expected)
    decimal_places = max(0, -Decimal(str(expected)).as_tuple().exponent)
    tolerance = float(Decimal("0.5") * (Decimal(10) ** -decimal_places))
    return math.isclose(float(actual), float(expected), rel_tol=0.0, abs_tol=tolerance)


def _answer_value_equal(actual: Any, expected: Any) -> bool:
    if isinstance(expected, bool):
        return isinstance(actual, bool) and actual is expected
    if _numeric_equal(actual, expected):
        return True
    if isinstance(expected, (tuple, list)):
        return isinstance(actual, (tuple, list)) and len(actual) == len(expected) and all(
            _answer_value_equal(actual_item, expected_item)
            for actual_item, expected_item in zip(actual, expected)
        )
    if isinstance(expected, Mapping):
        return (
            isinstance(actual, Mapping)
            and set(actual) == set(expected)
            and all(
                _answer_value_equal(actual[key], expected_value)
                for key, expected_value in expected.items()
            )
        )
    return actual == expected


def _answer_matches(answer: Mapping[str, Any], answer_key: Mapping[str, Any]) -> bool:
    return _answer_value_equal(answer, answer_key)


async def _wrong_attempt_count(
    db: AsyncSession,
    student_id: uuid.UUID,
    task_code: str,
) -> int:
    count = await db.scalar(
        select(func.count()).select_from(GameTaskAttempt).where(
            GameTaskAttempt.student_id == student_id,
            GameTaskAttempt.task_code == task_code,
            GameTaskAttempt.is_correct.is_(False),
        )
    )
    return int(count or 0)


async def _complete_lesson_if_ready(
    db: AsyncSession,
    progress: GameProgress,
    lesson_code: str,
) -> None:
    catalog = _catalog_for_progress(progress)
    lesson = _get_lesson(lesson_code, catalog)
    attempt = await _get_open_lesson_attempt(db, progress.student_id, lesson_code)
    if attempt is None:
        # Already finalized for this playthrough; nothing new to do.
        return

    # A replayed lesson's tasks already show a permanent result from an
    # earlier playthrough, so "is every task done" must be scoped to this
    # attempt (completed_at on/after it started), not to all history. A
    # first playthrough has no prior results to exclude, so the timestamp
    # filter must only apply on an actual replay -- otherwise re-entering
    # a still-incomplete lesson (which starts a fresh attempt) would
    # permanently strand any task already solved before the re-entry.
    results = (await db.execute(
        select(GameTaskResult).where(
            GameTaskResult.student_id == progress.student_id,
            GameTaskResult.task_code.in_(lesson.task_codes),
        )
    )).scalars().all()
    replaying = _is_replay(progress, lesson_code)
    resolved_this_attempt = {
        row.task_code: row.status
        for row in results
        if not replaying or row.completed_at >= attempt.started_at
    }
    if not set(lesson.task_codes).issubset(resolved_this_attempt):
        return

    any_assisted = (
        attempt.hints_used >= 5
        or any(status == "assisted" for status in resolved_this_attempt.values())
    )
    now = datetime.now(timezone.utc)
    attempt.status = "completed_with_stark_help" if any_assisted else "completed"
    attempt.completed_at = now

    completed_lessons = list(progress.completed_lesson_codes or [])
    if lesson_code not in completed_lessons:
        progress.completed_lesson_codes = [*completed_lessons, lesson_code]

    await game_rewards_service.finalize_lesson_result(
        db, progress.student_id, lesson_code, attempt, any_assisted, now,
    )
    await db.flush()
    await game_rewards_service.sync_achievements(db, progress.student_id)


async def submit_task_answer(
    db: AsyncSession,
    student_id: uuid.UUID,
    task_code: str,
    answer: Mapping[str, Any],
) -> TaskSubmission:
    progress = await _get_or_create_progress(db, student_id)
    catalog = _catalog_for_progress(progress)
    task = _get_task(task_code, catalog)
    _require_lesson_access(progress, _get_lesson(task.lesson_code, catalog), catalog)
    if not isinstance(answer, Mapping):
        raise InvalidAnswerError("Task answer must be an object")
    replaying = _is_replay(progress, task.lesson_code)
    existing = await db.get(GameTaskResult, (student_id, task_code))
    if existing is not None and not replaying:
        raise InvalidStateError(f"Task is already complete: {task_code}")
    await _require_task_learning(db, progress, task, catalog)
    attempt = await _current_lesson_attempt(db, student_id, task.lesson_code)
    correct = _answer_matches(answer, task.answer_key)
    if correct:
        db.add(
            GameTaskAttempt(
                student_id=student_id,
                task_code=task_code,
                answer=_json_answer(answer),
                is_correct=True,
            )
        )
        await _record_task_result(db, student_id, task_code, "solved", existing)
        await db.flush()
        await _complete_lesson_if_ready(db, progress, task.lesson_code)
        progress.current_node_code = task.next_node_code
        await db.flush()
        return TaskSubmission(
            correct=True,
            hint=None,
            help_available=False,
            status="solved",
            current_node_code=progress.current_node_code,
            lesson_hints_used=attempt.hints_used,
        )

    if await game_rewards_service.consume_attempt_stabilizer(db, student_id, task_code):
        await db.flush()
        return TaskSubmission(
            correct=False,
            hint=ATTEMPT_STABILIZER_HINT,
            help_available=attempt.hints_used >= 5,
            current_node_code=progress.current_node_code,
            lesson_hints_used=attempt.hints_used,
        )

    error_number = await _wrong_attempt_count(db, student_id, task_code) + 1
    usable_hints = tuple(
        hint for hint in task.hints if hint.level < _SOLUTION_HINT_LEVEL
    )
    hint = usable_hints[min(error_number, len(usable_hints)) - 1] if usable_hints else None
    db.add(
        GameTaskAttempt(
            student_id=student_id,
            task_code=task_code,
            answer=_json_answer(answer),
            is_correct=False,
            error_number=error_number,
            hint_code=(f"{task_code}-H{hint.level}" if hint else None),
        )
    )
    attempt.hints_used += 1
    stark_warning: dict[str, Any] | None = None
    if attempt.hints_used == 4 and not attempt.stark_warning_shown:
        attempt.stark_warning_shown = True
        stark_warning = {
            "shown": True,
            "text": STARK_WARNING_LINES[attempt.id.int % len(STARK_WARNING_LINES)],
        }
        await db.flush()
        await game_rewards_service.sync_achievements(db, student_id)
    if attempt.hints_used >= _SOLUTION_HINT_LEVEL:
        await _record_task_result(db, student_id, task_code, "assisted", existing)
        await db.flush()
        await _complete_lesson_if_ready(db, progress, task.lesson_code)
        progress.current_node_code = task.next_node_code
        await db.flush()
        return TaskSubmission(
            correct=False,
            hint=hint.text if hint else None,
            help_available=False,
            status="assisted",
            current_node_code=progress.current_node_code,
            lesson_hints_used=attempt.hints_used,
            stark_warning=stark_warning,
            solution=task.solution,
            consequence=task.consequence,
        )
    await db.flush()
    return TaskSubmission(
        correct=False,
        hint=hint.text if hint else None,
        help_available=attempt.hints_used >= 5,
        current_node_code=progress.current_node_code,
        lesson_hints_used=attempt.hints_used,
        stark_warning=stark_warning,
    )


async def purchase_shop_item(
    db: AsyncSession,
    student_id: uuid.UUID,
    item_id: str,
    task_code: str,
) -> game_rewards_service.ShopPurchaseResult:
    if item_id not in {"learning_replay", "astra_hint", "attempt_stabilizer"}:
        raise ContentNotFoundError(f"Unknown shop item: {item_id}")
    progress = await _get_or_create_progress(db, student_id)
    catalog = _catalog_for_progress(progress)
    task = _get_task(task_code, catalog)
    _require_lesson_access(progress, _get_lesson(task.lesson_code, catalog), catalog)
    replaying = _is_replay(progress, task.lesson_code)
    existing = await db.get(GameTaskResult, (student_id, task_code))
    if existing is not None and not replaying:
        raise InvalidStateError(f"Task is already complete: {task_code}")
    await _require_task_learning(db, progress, task, catalog)
    attempt = await _current_lesson_attempt(db, student_id, task.lesson_code)
    if item_id == "learning_replay":
        learning_node = _learning_node_for_task(task, catalog)
        return await game_rewards_service.purchase_learning_replay(
            db,
            student_id,
            task_code,
            learning_node_code=learning_node.code,
            book_card_id=getattr(task, "book_card_id", None),
            lesson_hints_used=attempt.hints_used,
        )
    if item_id == "attempt_stabilizer":
        return await game_rewards_service.purchase_attempt_stabilizer(
            db,
            student_id,
            task_code,
            lesson_hints_used=attempt.hints_used,
        )
    return await game_rewards_service.purchase_astra_hint(
        db,
        student_id,
        task_code,
        hint=_astra_hint_for_task(task),
        lesson_hints_used=attempt.hints_used,
    )


async def _record_task_result(
    db: AsyncSession, student_id: uuid.UUID, task_code: str, status: str,
    existing: GameTaskResult | None,
) -> None:
    if existing is not None:
        existing.status = status
        existing.completed_at = datetime.now(timezone.utc)
    else:
        db.add(GameTaskResult(student_id=student_id, task_code=task_code, status=status))


async def _require_task_learning(
    db: AsyncSession,
    progress: GameProgress,
    task: Any,
    catalog: ContentCatalog,
    *,
    require_current: bool = True,
) -> None:
    lesson = _get_lesson(task.lesson_code, catalog)
    _require_lesson_access(progress, lesson, catalog)
    if require_current:
        _require_current_node(progress, task.code)
    statuses = await _task_statuses(db, progress.student_id)
    if not set(lesson.task_codes[:lesson.task_codes.index(task.code)]).issubset(statuses):
        raise LockedContentError("Complete the preceding lesson tasks first")
    learning_nodes = [node for node in catalog.dialogue_nodes.values()
                      if getattr(node, "next_code", None) == task.code]
    if not learning_nodes:
        raise InvalidStateError("Task has no mini-learning scene")
    learning = await db.get(GameDialogueState, (progress.student_id, learning_nodes[0].code))
    if learning is None or learning.completed_at is None:
        raise InvalidStateError("Complete the task mini-learning first")


async def accept_stark_help(
    db: AsyncSession,
    student_id: uuid.UUID,
    task_code: str,
) -> StarkHelp:
    progress = await _get_or_create_progress(db, student_id)
    catalog = _catalog_for_progress(progress)
    task = _get_task(task_code, catalog)
    _require_lesson_access(progress, _get_lesson(task.lesson_code, catalog), catalog)
    replaying = _is_replay(progress, task.lesson_code)
    existing = await db.get(GameTaskResult, (student_id, task_code))
    if existing is not None and not replaying:
        raise InvalidStateError(f"Task is already complete: {task_code}")
    await _require_task_learning(db, progress, task, catalog)
    attempt = await _current_lesson_attempt(db, student_id, task.lesson_code)
    if attempt.hints_used < 5:
        raise LockedContentError("Stark help requires five wrong attempts in this lesson")

    await _record_task_result(db, student_id, task_code, "assisted", existing)
    await db.flush()
    await _complete_lesson_if_ready(db, progress, task.lesson_code)
    progress.current_node_code = task.next_node_code
    await db.flush()
    return StarkHelp(
        status="assisted",
        solution=task.solution,
        consequence=task.consequence,
        current_node_code=progress.current_node_code,
    )
