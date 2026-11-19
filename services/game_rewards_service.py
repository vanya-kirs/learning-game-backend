"""Wallet, ledger, lesson results, achievements and first-click tracking
for the Game rewards/currency layer.

Kept separate from services/learning_game_service.py so that module can
import from here (for lesson-completion/achievement hooks) without a
circular import; this module never imports learning_game_service.
"""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Mapping

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models_game import (
    GameAchievement,
    GameCurrencyLedgerEntry,
    GameDialogueState,
    GameFirstClick,
    GameLessonAttempt,
    GameLessonResult,
    GameProgress,
    GameWallet,
)
from services.game_content.achievements import ACHIEVEMENTS, ACHIEVEMENTS_BY_ID
from services.game_content.catalog import CATALOG
from services.game_content.first_clicks import FIRST_CLICK_TARGETS
from services.game_content.shop import SHOP_ITEMS, SHOP_ITEMS_BY_ID
from services.game_errors import ContentNotFoundError, InvalidStateError


_SUBJECTS = ("Информатика", "ИИ", "Робототехника")
_STAGES = (1, 2, 3, 4)


# --- Wallet -----------------------------------------------------------------

async def get_or_create_wallet(db: AsyncSession, student_id: uuid.UUID) -> GameWallet:
    await db.flush()
    await db.execute(
        insert(GameWallet)
        .values(student_id=student_id)
        .on_conflict_do_nothing(index_elements=[GameWallet.student_id])
    )
    return (await db.execute(
        select(GameWallet).where(GameWallet.student_id == student_id)
        .with_for_update().execution_options(populate_existing=True)
    )).scalar_one()


async def wallet_balance(db: AsyncSession, student_id: uuid.UUID) -> int:
    wallet = await get_or_create_wallet(db, student_id)
    return wallet.sircoins


async def _credit_wallet(
    db: AsyncSession,
    student_id: uuid.UUID,
    amount: int,
    *,
    reason: str,
    source_type: str,
    source_id: str | None = None,
) -> GameWallet:
    wallet = await get_or_create_wallet(db, student_id)
    wallet.sircoins += amount
    wallet.updated_at = datetime.now(timezone.utc)
    db.add(GameCurrencyLedgerEntry(
        id=uuid.uuid4(), student_id=student_id, delta=amount,
        reason=reason, source_type=source_type, source_id=source_id,
    ))
    await db.flush()
    return wallet


async def _debit_wallet(
    db: AsyncSession,
    wallet: GameWallet,
    amount: int,
    *,
    reason: str,
    source_type: str,
    source_id: str | None = None,
) -> GameWallet:
    if wallet.sircoins < amount:
        raise InvalidStateError("Not enough sircoins")
    wallet.sircoins -= amount
    wallet.updated_at = datetime.now(timezone.utc)
    db.add(GameCurrencyLedgerEntry(
        id=uuid.uuid4(), student_id=wallet.student_id, delta=-amount,
        reason=reason, source_type=source_type, source_id=source_id,
    ))
    await db.flush()
    return wallet


# --- Shop -------------------------------------------------------------------


async def shop_state(
    db: AsyncSession,
    student_id: uuid.UUID,
    *,
    current_task_code: str | None = None,
) -> dict[str, Any]:
    wallet = await get_or_create_wallet(db, student_id)
    purchased_source_ids = set((await db.execute(
        select(GameCurrencyLedgerEntry.source_id).where(
            GameCurrencyLedgerEntry.student_id == student_id,
            GameCurrencyLedgerEntry.source_type == "shop_purchase",
        )
    )).scalars())
    items: dict[str, dict[str, Any]] = {}
    for item in SHOP_ITEMS:
        source_id = f"{item.id}:{current_task_code}" if current_task_code else None
        purchased = (
            source_id in purchased_source_ids
            if source_id and item.id != "learning_replay"
            else False
        )
        used_source_id = (
            f"attempt_stabilizer_used:{current_task_code}"
            if current_task_code and item.id == "attempt_stabilizer"
            else None
        )
        active = (
            item.id == "attempt_stabilizer"
            and purchased
            and used_source_id not in purchased_source_ids
        )
        available = (
            item.enabled
            and current_task_code is not None
            and not purchased
            and wallet.sircoins >= item.price_sircoins
        )
        reason = None
        if not item.enabled:
            reason = "disabled"
        elif current_task_code is None:
            reason = "no_current_task"
        elif purchased:
            reason = "already_purchased"
        elif wallet.sircoins < item.price_sircoins:
            reason = "not_enough_sircoins"
        items[item.id] = {
            "available": available,
            "purchased": purchased,
            "active": active,
            "reason": reason,
        }
    return {
        "catalog": [
            {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "price_sircoins": item.price_sircoins,
                "enabled": item.enabled,
            }
            for item in SHOP_ITEMS
        ],
        "current_task": {
            "task_code": current_task_code,
            "items": items,
        },
    }


@dataclass(frozen=True)
class ShopPurchaseResult:
    item_id: str
    task_code: str
    price_sircoins: int
    sircoins: int
    hint: str | None
    lesson_hints_used: int
    learning_node_code: str | None = None
    book_card_id: str | None = None
    effect: str = "astra_hint"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


async def purchase_astra_hint(
    db: AsyncSession,
    student_id: uuid.UUID,
    task_code: str,
    *,
    hint: str,
    lesson_hints_used: int,
) -> ShopPurchaseResult:
    definition = SHOP_ITEMS_BY_ID.get("astra_hint")
    if definition is None or not definition.enabled:
        raise ContentNotFoundError("Unknown shop item: astra_hint")
    source_id = f"astra_hint:{task_code}"
    wallet = await get_or_create_wallet(db, student_id)
    existing = (await db.execute(
        select(GameCurrencyLedgerEntry).where(
            GameCurrencyLedgerEntry.student_id == student_id,
            GameCurrencyLedgerEntry.source_type == "shop_purchase",
            GameCurrencyLedgerEntry.source_id == source_id,
        )
    )).scalar_one_or_none()
    if existing is not None:
        raise InvalidStateError(f"Shop item is already purchased for task: {task_code}")
    wallet = await _debit_wallet(
        db,
        wallet,
        definition.price_sircoins,
        reason=f"Purchased {definition.id} for {task_code}",
        source_type="shop_purchase",
        source_id=source_id,
    )
    await sync_achievements(db, student_id)
    return ShopPurchaseResult(
        item_id=definition.id,
        task_code=task_code,
        price_sircoins=definition.price_sircoins,
        sircoins=wallet.sircoins,
        hint=hint,
        lesson_hints_used=lesson_hints_used,
        effect="astra_hint",
    )


async def purchase_learning_replay(
    db: AsyncSession,
    student_id: uuid.UUID,
    task_code: str,
    *,
    learning_node_code: str,
    book_card_id: str | None,
    lesson_hints_used: int,
) -> ShopPurchaseResult:
    definition = SHOP_ITEMS_BY_ID.get("learning_replay")
    if definition is None or not definition.enabled:
        raise ContentNotFoundError("Unknown shop item: learning_replay")
    wallet = await get_or_create_wallet(db, student_id)
    wallet = await _debit_wallet(
        db,
        wallet,
        definition.price_sircoins,
        reason=f"Purchased {definition.id} for {task_code}",
        source_type="shop_purchase",
        source_id=f"learning_replay:{task_code}:{uuid.uuid4().hex}",
    )
    await sync_achievements(db, student_id)
    return ShopPurchaseResult(
        item_id=definition.id,
        task_code=task_code,
        price_sircoins=definition.price_sircoins,
        sircoins=wallet.sircoins,
        hint=None,
        lesson_hints_used=lesson_hints_used,
        learning_node_code=learning_node_code,
        book_card_id=book_card_id,
        effect="learning_replay",
    )


async def purchase_attempt_stabilizer(
    db: AsyncSession,
    student_id: uuid.UUID,
    task_code: str,
    *,
    lesson_hints_used: int,
) -> ShopPurchaseResult:
    definition = SHOP_ITEMS_BY_ID.get("attempt_stabilizer")
    if definition is None or not definition.enabled:
        raise ContentNotFoundError("Unknown shop item: attempt_stabilizer")
    source_id = f"attempt_stabilizer:{task_code}"
    wallet = await get_or_create_wallet(db, student_id)
    existing = (await db.execute(
        select(GameCurrencyLedgerEntry).where(
            GameCurrencyLedgerEntry.student_id == student_id,
            GameCurrencyLedgerEntry.source_type == "shop_purchase",
            GameCurrencyLedgerEntry.source_id == source_id,
        )
    )).scalar_one_or_none()
    if existing is not None:
        raise InvalidStateError(f"Shop item is already purchased for task: {task_code}")
    wallet = await _debit_wallet(
        db,
        wallet,
        definition.price_sircoins,
        reason=f"Purchased {definition.id} for {task_code}",
        source_type="shop_purchase",
        source_id=source_id,
    )
    await sync_achievements(db, student_id)
    return ShopPurchaseResult(
        item_id=definition.id,
        task_code=task_code,
        price_sircoins=definition.price_sircoins,
        sircoins=wallet.sircoins,
        hint=None,
        lesson_hints_used=lesson_hints_used,
        effect="attempt_stabilizer_active",
    )


async def consume_attempt_stabilizer(
    db: AsyncSession,
    student_id: uuid.UUID,
    task_code: str,
) -> bool:
    purchase_source_id = f"attempt_stabilizer:{task_code}"
    used_source_id = f"attempt_stabilizer_used:{task_code}"
    rows = set((await db.execute(
        select(GameCurrencyLedgerEntry.source_id).where(
            GameCurrencyLedgerEntry.student_id == student_id,
            GameCurrencyLedgerEntry.source_type == "shop_purchase",
            GameCurrencyLedgerEntry.source_id.in_((purchase_source_id, used_source_id)),
        )
    )).scalars())
    if purchase_source_id not in rows or used_source_id in rows:
        return False
    db.add(GameCurrencyLedgerEntry(
        id=uuid.uuid4(),
        student_id=student_id,
        delta=0,
        reason=f"Consumed attempt_stabilizer for {task_code}",
        source_type="shop_purchase",
        source_id=used_source_id,
    ))
    await db.flush()
    return True


# --- First clicks -------------------------------------------------------------

async def first_click_state(db: AsyncSession, student_id: uuid.UUID) -> dict[str, bool]:
    seen = set((await db.execute(
        select(GameFirstClick.target_id).where(GameFirstClick.student_id == student_id)
    )).scalars())
    return {target: target in seen for target in sorted(FIRST_CLICK_TARGETS)}


async def record_first_click(db: AsyncSession, student_id: uuid.UUID, target_id: str) -> dict[str, bool]:
    if target_id not in FIRST_CLICK_TARGETS:
        raise ContentNotFoundError(f"Unknown first-click target: {target_id}")
    await db.execute(
        insert(GameFirstClick)
        .values(student_id=student_id, target_id=target_id)
        .on_conflict_do_nothing(index_elements=[GameFirstClick.student_id, GameFirstClick.target_id])
    )
    await db.flush()
    return await first_click_state(db, student_id)


# --- Lesson results -----------------------------------------------------------

def _result_rank(stars: int | None, kind: str) -> int:
    if kind == "stark_help":
        return 0
    return 1 + (stars or 0)


async def lesson_results_state(db: AsyncSession, student_id: uuid.UUID) -> dict[str, dict[str, Any]]:
    rows = (await db.execute(
        select(GameLessonResult).where(GameLessonResult.student_id == student_id)
    )).scalars()
    return {
        row.lesson_code: {
            "best_result_kind": row.best_result_kind,
            "best_stars": row.best_stars,
            "best_hints_used": row.best_hints_used,
            "last_result_kind": row.last_result_kind,
            "last_stars": row.last_stars,
            "last_hints_used": row.last_hints_used,
            "completed_attempts": row.completed_attempts,
        }
        for row in rows
    }


async def finalize_lesson_result(
    db: AsyncSession,
    student_id: uuid.UUID,
    lesson_code: str,
    attempt: GameLessonAttempt,
    any_assisted: bool,
    now: datetime,
) -> None:
    stars = None if any_assisted else max(0, 3 - attempt.hints_used)
    kind = "stark_help" if any_assisted else "stars"
    existing = await db.get(GameLessonResult, (student_id, lesson_code))
    if existing is None:
        db.add(GameLessonResult(
            student_id=student_id, lesson_code=lesson_code,
            best_stars=stars, best_result_kind=kind,
            best_hints_used=attempt.hints_used, best_completed_at=now,
            last_stars=stars, last_result_kind=kind,
            last_hints_used=attempt.hints_used, last_completed_at=now,
            completed_attempts=1,
        ))
        await db.flush()
        return
    existing.last_stars = stars
    existing.last_result_kind = kind
    existing.last_hints_used = attempt.hints_used
    existing.last_completed_at = now
    existing.completed_attempts += 1
    if _result_rank(stars, kind) > _result_rank(existing.best_stars, existing.best_result_kind):
        existing.best_stars = stars
        existing.best_result_kind = kind
        existing.best_hints_used = attempt.hints_used
        existing.best_completed_at = now
    await db.flush()


# --- Achievements ---------------------------------------------------------------

@dataclass(frozen=True)
class _AchievementContext:
    completed_lesson_codes: frozenset[str]
    lesson_results: Mapping[str, GameLessonResult]
    already_earned: frozenset[str]
    claimed_count: int
    shop_purchase_count: int
    intro_astra_done: bool
    warning_ever_shown: bool
    recent_attempts: tuple[GameLessonAttempt, ...]  # newest first


def _stage_subject_lesson_codes(stage: int, subject: str) -> set[str]:
    return {lesson.code for lesson in CATALOG.stage_lessons(stage) if lesson.subject == subject}


def _any_stage_subject_complete(ctx: _AchievementContext, subject: str) -> bool:
    return any(
        (codes := _stage_subject_lesson_codes(stage, subject)) and codes.issubset(ctx.completed_lesson_codes)
        for stage in _STAGES
    )


def _any_stage_complete(ctx: _AchievementContext) -> bool:
    return any(
        (codes := set(CATALOG.stage_lesson_codes(stage))) and codes.issubset(ctx.completed_lesson_codes)
        for stage in _STAGES
    )


def _all_stages_complete(ctx: _AchievementContext) -> bool:
    stage_codes = [set(CATALOG.stage_lesson_codes(stage)) for stage in _STAGES]
    if any(not codes for codes in stage_codes):
        return False  # stage has no content yet — branch cannot be "complete"
    return all(codes.issubset(ctx.completed_lesson_codes) for codes in stage_codes)


def _perfect_subject_stage(ctx: _AchievementContext) -> bool:
    for stage in _STAGES:
        for subject in _SUBJECTS:
            codes = _stage_subject_lesson_codes(stage, subject)
            if len(codes) < 2:
                continue
            three_star = sum(
                1 for code in codes
                if (result := ctx.lesson_results.get(code)) and result.best_stars == 3
            )
            if three_star >= 2:
                return True
    return False


def _perfect_stage(ctx: _AchievementContext) -> bool:
    for stage in _STAGES:
        codes = set(CATALOG.stage_lesson_codes(stage))
        if not codes:
            continue
        if all(
            (result := ctx.lesson_results.get(code)) and result.best_stars == 3
            for code in codes
        ):
            return True
    return False


def _independent_streak_5(ctx: _AchievementContext) -> bool:
    streak = 0
    for attempt in ctx.recent_attempts:
        if attempt.status == "completed" and attempt.hints_used == 0:
            streak += 1
            if streak >= 5:
                return True
        else:
            break
    return False


def _three_stars_any(ctx: _AchievementContext) -> bool:
    return any(result.best_stars == 3 for result in ctx.lesson_results.values())


def _no_hints_lesson(ctx: _AchievementContext) -> bool:
    return any(
        result.best_result_kind == "stars" and result.best_hints_used == 0
        for result in ctx.lesson_results.values()
    )


def _completed_with_stark_help(ctx: _AchievementContext) -> bool:
    return any(result.best_result_kind == "stark_help" for result in ctx.lesson_results.values())


def _improved_replay(ctx: _AchievementContext) -> bool:
    return any(
        result.completed_attempts > 1 and result.best_completed_at == result.last_completed_at
        for result in ctx.lesson_results.values()
    )


def _last_chance_solved(ctx: _AchievementContext) -> bool:
    return any(
        result.last_result_kind == "stars" and result.last_hints_used == 4
        for result in ctx.lesson_results.values()
    )


_PREDICATES: dict[str, Callable[[_AchievementContext], bool]] = {
    "intro_astra": lambda ctx: ctx.intro_astra_done,
    "first_lesson": lambda ctx: bool(ctx.completed_lesson_codes),
    "first_trophy_claim": lambda ctx: ctx.claimed_count >= 1,
    "three_stars_any": _three_stars_any,
    "no_hints_lesson": _no_hints_lesson,
    "perfect_subject_stage": _perfect_subject_stage,
    "perfect_stage": _perfect_stage,
    "independent_streak_5": _independent_streak_5,
    "dispatch_restored": lambda ctx: _any_stage_subject_complete(ctx, "Информатика"),
    "server_restored": lambda ctx: _any_stage_subject_complete(ctx, "ИИ"),
    "mining_restored": lambda ctx: _any_stage_subject_complete(ctx, "Робототехника"),
    "stage_complete": _any_stage_complete,
    "stark_branch_complete": _all_stages_complete,
    "completed_with_stark_help": _completed_with_stark_help,
    "last_chance_solved": _last_chance_solved,
    "improved_replay": _improved_replay,
    "stark_warning_seen": lambda ctx: ctx.warning_ever_shown,
    "first_shop_purchase": lambda ctx: ctx.shop_purchase_count >= 1,
}


async def _build_context(db: AsyncSession, student_id: uuid.UUID) -> _AchievementContext:
    progress = await db.get(GameProgress, student_id)
    completed = frozenset(progress.completed_lesson_codes or []) if progress else frozenset()

    results = (await db.execute(
        select(GameLessonResult).where(GameLessonResult.student_id == student_id)
    )).scalars().all()
    lesson_results = {row.lesson_code: row for row in results}

    earned = frozenset((await db.execute(
        select(GameAchievement.achievement_id).where(GameAchievement.student_id == student_id)
    )).scalars())

    claimed_count = await db.scalar(
        select(func.count()).select_from(GameAchievement).where(
            GameAchievement.student_id == student_id,
            GameAchievement.status == "claimed",
        )
    )

    shop_purchase_count = await db.scalar(
        select(func.count()).select_from(GameCurrencyLedgerEntry).where(
            GameCurrencyLedgerEntry.student_id == student_id,
            GameCurrencyLedgerEntry.source_type == "shop_purchase",
        )
    )

    astra_state = await db.get(GameDialogueState, (student_id, "ПР-01"))
    intro_astra_done = astra_state is not None and astra_state.completed_at is not None

    warning_count = await db.scalar(
        select(func.count()).select_from(GameLessonAttempt).where(
            GameLessonAttempt.student_id == student_id,
            GameLessonAttempt.stark_warning_shown.is_(True),
        )
    )

    recent = (await db.execute(
        select(GameLessonAttempt).where(
            GameLessonAttempt.student_id == student_id,
            GameLessonAttempt.status.in_(("completed", "completed_with_stark_help")),
        ).order_by(GameLessonAttempt.completed_at.desc()).limit(10)
    )).scalars().all()

    return _AchievementContext(
        completed_lesson_codes=completed,
        lesson_results=lesson_results,
        already_earned=earned,
        claimed_count=int(claimed_count or 0),
        shop_purchase_count=int(shop_purchase_count or 0),
        intro_astra_done=intro_astra_done,
        warning_ever_shown=bool(warning_count),
        recent_attempts=tuple(recent),
    )


async def sync_achievements(db: AsyncSession, student_id: uuid.UUID) -> tuple[str, ...]:
    """Re-evaluate every enabled achievement predicate and grant new ones.

    Idempotent and cheap to call after any event that could satisfy a
    predicate (lesson finalized, warning shown, achievement claimed,
    ПР-01 dialogue completed) — the catalog and a student's data are both
    small, and re-evaluating everything avoids needing per-achievement
    event wiring.
    """
    ctx = await _build_context(db, student_id)
    now = datetime.now(timezone.utc)
    newly_earned: list[str] = []
    for definition in ACHIEVEMENTS:
        if not definition.enabled or definition.id in ctx.already_earned:
            continue
        predicate = _PREDICATES.get(definition.id)
        if predicate is None or not predicate(ctx):
            continue
        db.add(GameAchievement(
            student_id=student_id, achievement_id=definition.id,
            status="earned_unclaimed", earned_at=now,
            reward_sircoins=definition.reward_sircoins,
        ))
        newly_earned.append(definition.id)
    if newly_earned:
        await db.flush()
    return tuple(newly_earned)


async def achievement_progress_state(db: AsyncSession, student_id: uuid.UUID) -> dict[str, dict[str, Any]]:
    rows = (await db.execute(
        select(GameAchievement).where(GameAchievement.student_id == student_id)
    )).scalars()
    return {
        row.achievement_id: {
            "status": row.status,
            "earned_at": row.earned_at,
            "claimed_at": row.claimed_at,
        }
        for row in rows
    }


@dataclass(frozen=True)
class AchievementClaimResult:
    achievement_id: str
    status: str
    reward_sircoins: int
    sircoins: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


async def claim_achievement(
    db: AsyncSession, student_id: uuid.UUID, achievement_id: str
) -> AchievementClaimResult:
    definition = ACHIEVEMENTS_BY_ID.get(achievement_id)
    if definition is None or not definition.enabled:
        raise ContentNotFoundError(f"Unknown achievement: {achievement_id}")
    row = (await db.execute(
        select(GameAchievement)
        .where(
            GameAchievement.student_id == student_id,
            GameAchievement.achievement_id == achievement_id,
        )
        .with_for_update()
    )).scalar_one_or_none()
    if row is None:
        raise InvalidStateError(f"Achievement is not earned yet: {achievement_id}")
    if row.status == "claimed":
        wallet = await get_or_create_wallet(db, student_id)
        return AchievementClaimResult(achievement_id, "claimed", row.reward_sircoins, wallet.sircoins)

    row.status = "claimed"
    row.claimed_at = datetime.now(timezone.utc)
    wallet = await _credit_wallet(
        db, student_id, row.reward_sircoins,
        reason=f"Claimed achievement {achievement_id}",
        source_type="achievement_claim",
        source_id=achievement_id,
    )
    await sync_achievements(db, student_id)
    return AchievementClaimResult(achievement_id, "claimed", row.reward_sircoins, wallet.sircoins)
