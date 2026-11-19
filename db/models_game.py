from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class GameProgress(Base):
    """Current server-driven Game location and progression facts."""

    __tablename__ = "game_progress"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    current_node_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    ddo_profile: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    ddo_scores: Mapped[Optional[dict[str, int]]] = mapped_column(JSON, nullable=True)
    ddo_dominant_codes: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    completed_lesson_codes: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        server_default=text("'[]'::json"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class GameDialogueState(Base):
    """Per-node dialogue history; story choices do not affect diagnostics."""

    __tablename__ = "game_dialogue_states"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    node_code: Mapped[str] = mapped_column(String(64), primary_key=True)
    viewed_question_codes: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        server_default=text("'[]'::json"),
    )
    selected_choice_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    action_state: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class GameTaskAttempt(Base):
    """Immutable history of submitted task answers and issued hints."""

    __tablename__ = "game_task_attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    task_code: Mapped[str] = mapped_column(String(32), nullable=False)
    answer: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_correct: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    error_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    hint_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (
        Index("ix_game_task_attempts_student_task", "student_id", "task_code"),
    )


class GameTaskResult(Base):
    """Terminal task outcome; a student completes each task only once."""

    __tablename__ = "game_task_results"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    task_code: Mapped[str] = mapped_column(String(32), primary_key=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('solved', 'assisted')",
            name="ck_game_task_results_status",
        ),
    )


class GameBookEntry(Base):
    """A digital-book card unlocked for one student."""

    __tablename__ = "game_book_entries"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    book_card_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class GameWallet(Base):
    """Одна строка на ученика — баланс сиркоинов."""

    __tablename__ = "game_wallets"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    sircoins: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (
        CheckConstraint("sircoins >= 0", name="ck_game_wallets_non_negative"),
    )


class GameCurrencyLedgerEntry(Base):
    """Журнал начислений/списаний сиркоинов, для разбора спорных случаев."""

    __tablename__ = "game_currency_ledger"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=False)
    source_type: Mapped[str] = mapped_column(String, nullable=False)
    source_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (
        CheckConstraint(
            "source_type IN ('lesson_completion', 'achievement_claim', 'shop_purchase', 'admin_adjustment')",
            name="ck_game_currency_ledger_source_type",
        ),
        Index("ix_game_currency_ledger_student", "student_id"),
    )


class GameLessonResult(Base):
    """Лучший и последний результат прохождения занятия."""

    __tablename__ = "game_lesson_results"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    lesson_code: Mapped[str] = mapped_column(String(64), primary_key=True)
    best_stars: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    best_result_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    best_hints_used: Mapped[int] = mapped_column(Integer, nullable=False)
    best_completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_stars: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_result_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    last_hints_used: Mapped[int] = mapped_column(Integer, nullable=False)
    last_completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))

    __table_args__ = (
        CheckConstraint(
            "best_result_kind IN ('stars', 'stark_help')", name="ck_game_lesson_results_best_kind"
        ),
        CheckConstraint(
            "last_result_kind IN ('stars', 'stark_help')", name="ck_game_lesson_results_last_kind"
        ),
    )


class GameLessonAttempt(Base):
    """Текущая (in_progress) или историческая попытка прохождения занятия.

    A fresh row is created every time enter_lesson() runs for this
    (student, lesson); any prior in_progress row for the same lesson is
    marked 'abandoned' first, so exactly one row per lesson stays
    in_progress at a time. hints_used counts wrong task answers across the
    whole lesson while this row is in_progress (spec 3.4).
    """

    __tablename__ = "game_lesson_attempts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    lesson_code: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    hints_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    stark_warning_shown: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('in_progress', 'completed', 'completed_with_stark_help', 'abandoned')",
            name="ck_game_lesson_attempts_status",
        ),
        Index(
            "ix_game_lesson_attempts_student_lesson_status",
            "student_id", "lesson_code", "status",
        ),
        Index(
            "ux_game_lesson_attempts_open",
            "student_id", "lesson_code",
            unique=True,
            postgresql_where=text("status = 'in_progress'"),
        ),
    )


class GameAchievement(Base):
    """Статус ачивки у ученика — earned_unclaimed до claim, затем claimed."""

    __tablename__ = "game_achievements"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    achievement_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    claimed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reward_sircoins: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('earned_unclaimed', 'claimed')", name="ck_game_achievements_status"
        ),
    )


class GameFirstClick(Base):
    """Отметка, что first-click объяснение Астры для объекта уже показано."""

    __tablename__ = "game_first_clicks"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    target_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
