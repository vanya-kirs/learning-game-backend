"""Authenticated HTTP contract for the Game game MVP."""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Mapping
from math import isfinite
from typing import Any, TypeVar

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas.learning_game import (
    AdvanceRequest,
    AchievementClaimResponse,
    DialogueChoiceRequest,
    DialogueResponse,
    FirstClickResponse,
    GameStateResponse,
    InterfaceActionRequest,
    InterfaceActionResponse,
    KlimovResponse,
    KlimovSubmitRequest,
    SceneTransitionResponse,
    ShopPurchaseRequest,
    ShopPurchaseResponse,
    TaskAnswerPayload,
    TaskAnswerResponse,
    TaskHelpResponse,
)
from core.security_web import WebContext, get_web_context, require_scope
from db.session import get_session
from services import learning_game_service, game_rewards_service
from services.game_content.catalog import public_answer_schema
from services.game_content.onboarding import ONBOARDING_NODES
from services.learning_game_service import (
    ContentNotFoundError,
    InvalidAnswerError,
    InvalidStateError,
    LockedContentError,
)


web_game_router = APIRouter(tags=["learning-game"])

_ResultT = TypeVar("_ResultT")
_ONBOARDING_NODE_CODES = frozenset(node.code for node in ONBOARDING_NODES)
_ONBOARDING_NEXT_CODES = {
    node.code: ONBOARDING_NODES[index + 1].code
    for index, node in enumerate(ONBOARDING_NODES[:-1])
}
_ONBOARDING_NEXT_CODES["ПР-07"] = "stage_hub"


class _AnswerSchemaError(ValueError):
    pass


def _student_id(ctx: WebContext) -> uuid.UUID:
    return uuid.UUID(ctx.user_id)


async def _commit_domain_result(
    db: AsyncSession,
    operation: Awaitable[_ResultT],
) -> _ResultT:
    try:
        result = await operation
    except LockedContentError as exc:
        await db.rollback()
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ContentNotFoundError as exc:
        await db.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidStateError as exc:
        await db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except InvalidAnswerError as exc:
        await db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    await db.commit()
    return result


def _payload(result: Any) -> dict[str, Any]:
    return result.as_dict()


def _dialogue_item_payload(item: Mapping[str, str]) -> dict[str, str]:
    return {
        key: item[key]
        for key in ("code", "text", "response", "next_code")
        if key in item
    }


def _dialogue_node_payload(node: Any) -> dict[str, Any]:
    next_code = getattr(node, "next_code", "") or _ONBOARDING_NEXT_CODES.get(node.code)
    actions = [
        {
            "id": action.id,
            "from_state": action.from_state,
            "to_state": action.to_state,
            "instruction": action.instruction,
        }
        for action in getattr(node, "actions", ())
    ]
    return {
        "code": node.code,
        "mode": node.mode,
        "lines": list(node.lines),
        "questions": [_dialogue_item_payload(item) for item in node.questions],
        "choices": [_dialogue_item_payload(item) for item in node.choices],
        "continue_label": node.continue_label,
        "next_code": next_code,
        "initial_state": getattr(node, "initial_state", None),
        "completed_state": getattr(node, "completed_state", None),
        "actions": actions,
    }


def _node_is_available(node: Any, state: Any) -> bool:
    if node.code in _ONBOARDING_NODE_CODES:
        return state.ddo_profile is not None or node.code not in {"ПР-05", "ПР-06", "ПР-07"}

    lesson_code = getattr(node, "lesson_code", "")
    if lesson_code and lesson_code not in state.available_lessons:
        return False

    completed_lessons = set(state.completed_lesson_codes)
    if not set(getattr(node, "required_lesson_codes", ())).issubset(completed_lessons):
        return False

    completed_tasks = set(state.task_statuses)
    return set(getattr(node, "required_task_codes", ())).issubset(completed_tasks)


def _content_payload(state: Any) -> dict[str, Any]:
    catalog = learning_game_service.catalog_for_profile(state.ddo_profile)
    available_lesson_codes = set(state.available_lessons)
    lessons = {
        code: {
            "code": lesson.code,
            "stage": lesson.stage,
            "subject": lesson.subject,
            "number": lesson.number,
            "title": lesson.title,
            "prerequisite_codes": list(lesson.prerequisite_codes),
            "dialogue_node_codes": list(lesson.dialogue_node_codes),
            "task_codes": list(lesson.task_codes),
            "book_card_ids": list(lesson.book_card_ids),
        }
        for code, lesson in catalog.lessons.items()
        if code in available_lesson_codes
    }
    dialogue_nodes = {
        code: _dialogue_node_payload(node)
        for code, node in catalog.dialogue_nodes.items()
        if _node_is_available(node, state)
    }
    tasks = {
        code: catalog.public_task(code)
        for code, task in catalog.tasks.items()
        if task.lesson_code in available_lesson_codes
    }
    book_cards = {
        card_id: {
            "id": card.id,
            "stage": card.stage,
            "subject": card.subject,
            "lesson_code": card.lesson_code,
            "title": card.title,
            "content": list(card.content),
        }
        for card_id in state.unlocked_book_cards
        if (card := catalog.book_cards.get(card_id)) is not None
    }
    return {
        "lessons": lessons,
        "dialogue_nodes": dialogue_nodes,
        "tasks": tasks,
        "book_cards": book_cards,
    }


def _achievement_catalog_payload() -> list[dict[str, Any]]:
    from services.game_content.achievements import ACHIEVEMENTS

    return [
        {
            "id": item.id,
            "category": item.category,
            "title": item.title,
            "description": item.description,
            "reward_sircoins": item.reward_sircoins,
            "enabled": item.enabled,
        }
        for item in ACHIEVEMENTS
    ]


def _state_payload(state: Any) -> dict[str, Any]:
    payload = _payload(state)
    payload["content"] = _content_payload(state)
    payload["economy"] = {"sircoins": payload.pop("sircoins")}
    payload["achievements"] = {
        "catalog": _achievement_catalog_payload(),
        "progress": payload.pop("achievement_progress"),
    }
    return payload




def _is_json_type(value: Any, expected_type: str) -> bool:
    if expected_type == "null":
        return value is None
    if expected_type == "boolean":
        return type(value) is bool
    if expected_type == "integer":
        return type(value) is int
    if expected_type == "number":
        return type(value) is int or (type(value) is float and isfinite(value))
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "object":
        return isinstance(value, dict)
    return False


def _validate_answer_value(value: Any, schema: Mapping[str, Any], path: str) -> None:
    any_of = schema.get("anyOf")
    if any_of is not None:
        for option in any_of:
            try:
                _validate_answer_value(value, option, path)
            except _AnswerSchemaError:
                continue
            return
        raise _AnswerSchemaError(f"{path} does not match any allowed type")

    expected = schema.get("type")
    expected_types = (expected,) if isinstance(expected, str) else tuple(expected or ())
    if expected_types and not any(
        _is_json_type(value, expected_type) for expected_type in expected_types
    ):
        raise _AnswerSchemaError(f"{path} has the wrong type")

    if "enum" in schema and value not in schema["enum"]:
        raise _AnswerSchemaError(f"{path} has an unsupported value")

    if isinstance(value, str) and len(value) < int(schema.get("minLength", 0)):
        raise _AnswerSchemaError(f"{path} is too short")

    if isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            _validate_answer_value(item, schema["items"], f"{path}[{index}]")

    if isinstance(value, dict) and "properties" in schema:
        properties = schema["properties"]
        required = set(schema.get("required", ()))
        missing = required - set(value)
        extra = set(value) - set(properties)
        if missing:
            raise _AnswerSchemaError(f"{path} is missing required fields")
        if extra:
            raise _AnswerSchemaError(f"{path} contains unexpected fields")
        for key, item in value.items():
            _validate_answer_value(item, properties[key], f"{path}.{key}")


def _validated_private_answer(task_code: str, body: TaskAnswerPayload) -> dict[str, Any]:
    try:
        catalog = learning_game_service.catalog_for_task_code(task_code)
        task = catalog.task(task_code)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown task: {task_code}") from exc

    try:
        _validate_answer_value(body, public_answer_schema(task), "answer")
    except _AnswerSchemaError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if not isinstance(task.answer_key, Mapping):
        raise RuntimeError(f"Game task has a non-object answer key: {task_code}")
    return {key: body[key] for key in task.answer_key}






@web_game_router.get("/web/game/state", response_model=GameStateResponse)
async def get_game_state(
    db: AsyncSession = Depends(get_session),
    ctx: WebContext = Depends(get_web_context),
) -> dict[str, Any]:
    require_scope(ctx, "student:own")
    state = await _commit_domain_result(
        db,
        learning_game_service.get_state(db, _student_id(ctx)),
    )
    return _state_payload(state)


@web_game_router.post("/web/game/advance", response_model=SceneTransitionResponse)
async def advance_game_scene(
    body: AdvanceRequest,
    db: AsyncSession = Depends(get_session),
    ctx: WebContext = Depends(get_web_context),
) -> dict[str, Any]:
    require_scope(ctx, "student:own")
    transition = await _commit_domain_result(
        db,
        learning_game_service.advance_scene(db, _student_id(ctx), body.node_code),
    )
    return _payload(transition)


@web_game_router.post(
    "/web/game/dialogues/{node_code}/questions/{question_code}",
    response_model=DialogueResponse,
    response_model_exclude_none=True,
)
async def view_dialogue_question(
    node_code: str,
    question_code: str,
    db: AsyncSession = Depends(get_session),
    ctx: WebContext = Depends(get_web_context),
) -> dict[str, str]:
    require_scope(ctx, "student:own")
    return await _commit_domain_result(
        db,
        learning_game_service.view_question(
            db,
            _student_id(ctx),
            node_code,
            question_code,
        ),
    )


@web_game_router.post(
    "/web/game/dialogues/{node_code}/choice",
    response_model=DialogueResponse,
    response_model_exclude_none=True,
)
async def select_dialogue_choice(
    node_code: str,
    body: DialogueChoiceRequest,
    db: AsyncSession = Depends(get_session),
    ctx: WebContext = Depends(get_web_context),
) -> dict[str, str]:
    require_scope(ctx, "student:own")
    return await _commit_domain_result(
        db,
        learning_game_service.select_option(
            db,
            _student_id(ctx),
            node_code,
            body.choice_code,
        ),
    )


@web_game_router.post(
    "/web/game/dialogues/{node_code}/action",
    response_model=InterfaceActionResponse,
)
async def perform_interface_action(
    node_code: str,
    body: InterfaceActionRequest,
    db: AsyncSession = Depends(get_session),
    ctx: WebContext = Depends(get_web_context),
) -> dict[str, Any]:
    require_scope(ctx, "student:own")
    return await _commit_domain_result(
        db,
        learning_game_service.perform_action(db, _student_id(ctx), node_code, body.action_id),
    )


@web_game_router.post(
    "/web/game/onboarding/klimov",
    response_model=KlimovResponse,
)
async def submit_klimov(
    body: KlimovSubmitRequest,
    db: AsyncSession = Depends(get_session),
    ctx: WebContext = Depends(get_web_context),
) -> dict[str, Any]:
    require_scope(ctx, "student:own")
    state = await _commit_domain_result(
        db,
        learning_game_service.submit_klimov(
            db,
            _student_id(ctx),
            body.domain_submission(),
        ),
    )
    return _state_payload(state)


@web_game_router.post(
    "/web/game/lessons/{lesson_code}/enter",
    response_model=SceneTransitionResponse,
)
async def enter_lesson(
    lesson_code: str,
    db: AsyncSession = Depends(get_session),
    ctx: WebContext = Depends(get_web_context),
) -> dict[str, Any]:
    require_scope(ctx, "student:own")
    transition = await _commit_domain_result(
        db,
        learning_game_service.enter_lesson(db, _student_id(ctx), lesson_code),
    )
    return _payload(transition)


@web_game_router.post(
    "/web/game/tasks/{task_code}/answer",
    response_model=TaskAnswerResponse,
)
async def submit_task_answer(
    task_code: str,
    body: TaskAnswerPayload,
    db: AsyncSession = Depends(get_session),
    ctx: WebContext = Depends(get_web_context),
) -> dict[str, Any]:
    require_scope(ctx, "student:own")
    answer = _validated_private_answer(task_code, body)
    result = await _commit_domain_result(
        db,
        learning_game_service.submit_task_answer(
            db,
            _student_id(ctx),
            task_code,
            answer,
        ),
    )
    return _payload(result)


@web_game_router.post(
    "/web/game/tasks/{task_code}/help",
    response_model=TaskHelpResponse,
)
async def accept_stark_help(
    task_code: str,
    db: AsyncSession = Depends(get_session),
    ctx: WebContext = Depends(get_web_context),
) -> dict[str, Any]:
    require_scope(ctx, "student:own")
    result = await _commit_domain_result(
        db,
        learning_game_service.accept_stark_help(db, _student_id(ctx), task_code),
    )
    return _payload(result)


@web_game_router.post(
    "/web/game/shop/{item_id}/purchase",
    response_model=ShopPurchaseResponse,
)
async def purchase_shop_item(
    item_id: str,
    body: ShopPurchaseRequest,
    db: AsyncSession = Depends(get_session),
    ctx: WebContext = Depends(get_web_context),
) -> dict[str, Any]:
    require_scope(ctx, "student:own")
    result = await _commit_domain_result(
        db,
        learning_game_service.purchase_shop_item(
            db,
            _student_id(ctx),
            item_id,
            body.task_code,
        ),
    )
    return _payload(result)


@web_game_router.post(
    "/web/game/first-clicks/{target_id}",
    response_model=FirstClickResponse,
)
async def mark_first_click(
    target_id: str,
    db: AsyncSession = Depends(get_session),
    ctx: WebContext = Depends(get_web_context),
) -> dict[str, Any]:
    require_scope(ctx, "student:own")
    seen = await _commit_domain_result(
        db,
        game_rewards_service.record_first_click(db, _student_id(ctx), target_id),
    )
    return {"first_click_seen": seen}


@web_game_router.post(
    "/web/game/achievements/{achievement_id}/claim",
    response_model=AchievementClaimResponse,
)
async def claim_achievement(
    achievement_id: str,
    db: AsyncSession = Depends(get_session),
    ctx: WebContext = Depends(get_web_context),
) -> dict[str, Any]:
    require_scope(ctx, "student:own")
    result = await _commit_domain_result(
        db,
        game_rewards_service.claim_achievement(db, _student_id(ctx), achievement_id),
    )
    return _payload(result)
