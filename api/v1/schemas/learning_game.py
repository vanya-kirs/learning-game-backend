"""Public request and response models for the Game game API."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


KlimovProfile = Literal["chp", "cht", "chch", "chz", "chkh"]
ContentStatus = Literal["available", "locked", "soon"]
TaskStatus = Literal["solved", "assisted"]


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MapLocationResponse(_StrictModel):
    profile: str
    mentor: str
    title: str
    description: str
    status: ContentStatus
    image_asset: str | None = None
    mentor_asset: str | None = None
    local_astra_point: str | None = None
    map_points: list[dict[str, str]] = Field(default_factory=list)


class PublicLessonResponse(_StrictModel):
    code: str
    stage: int
    subject: str
    number: int
    title: str
    prerequisite_codes: list[str]
    dialogue_node_codes: list[str]
    task_codes: list[str]
    book_card_ids: list[str]


class DialogueActionResponse(_StrictModel):
    id: str
    from_state: str
    to_state: str
    instruction: str


class PublicDialogueItemResponse(_StrictModel):
    code: str
    text: str
    response: str
    next_code: str | None = None


class PublicDialogueNodeResponse(_StrictModel):
    code: str
    mode: str
    lines: list[str]
    questions: list[PublicDialogueItemResponse]
    choices: list[PublicDialogueItemResponse]
    continue_label: str
    next_code: str | None = None
    initial_state: str | None = None
    completed_state: str | None = None
    actions: list[DialogueActionResponse] = Field(default_factory=list)


class PublicHintResponse(_StrictModel):
    level: int
    text: str


class PublicTaskResponse(_StrictModel):
    code: str
    stage: int
    subject: str
    lesson_code: str
    number: int
    prompt: str
    input_schema: dict[str, Any]
    hints: list[PublicHintResponse]
    book_card_id: str


class PublicBookCardResponse(_StrictModel):
    id: str
    stage: int
    subject: str
    lesson_code: str
    title: str
    content: list[str]


class DialogueStateResponse(_StrictModel):
    viewed_question_codes: list[str]
    selected_choice_code: str | None
    action_state: str | None
    completed: bool


class IssuedHintResponse(PublicHintResponse):
    code: str


class TaskProgressResponse(_StrictModel):
    wrong_attempt_count: int
    issued_hints: list[IssuedHintResponse]
    help_available: bool


class GrowthCharacteristicResponse(_StrictModel):
    profile: KlimovProfile
    code: str
    title: str
    score: int
    max_score: int
    source: Literal["klimov_ddo"]


class GrowthHallResponse(_StrictModel):
    is_enabled: bool
    status: Literal["future"]
    characteristics: list[GrowthCharacteristicResponse]


class GameContentResponse(_StrictModel):
    lessons: dict[str, PublicLessonResponse]
    dialogue_nodes: dict[str, PublicDialogueNodeResponse]
    tasks: dict[str, PublicTaskResponse]
    book_cards: dict[str, PublicBookCardResponse]


class EconomyResponse(_StrictModel):
    sircoins: int


class ShopCatalogItemResponse(_StrictModel):
    id: str
    title: str
    description: str
    price_sircoins: int
    enabled: bool


class ShopItemStateResponse(_StrictModel):
    available: bool
    purchased: bool
    active: bool = False
    reason: str | None = None


class CurrentTaskShopResponse(_StrictModel):
    task_code: str | None
    items: dict[str, ShopItemStateResponse]


class ShopStateResponse(_StrictModel):
    catalog: list[ShopCatalogItemResponse]
    current_task: CurrentTaskShopResponse


ResultKind = Literal["stars", "stark_help"]


class LessonResultResponse(_StrictModel):
    best_result_kind: ResultKind
    best_stars: int | None
    best_hints_used: int
    last_result_kind: ResultKind
    last_stars: int | None
    last_hints_used: int
    completed_attempts: int


class AchievementCatalogEntryResponse(_StrictModel):
    id: str
    category: str
    title: str
    description: str
    reward_sircoins: int
    enabled: bool


class AchievementProgressResponse(_StrictModel):
    status: Literal["earned_unclaimed", "claimed"]
    earned_at: datetime
    claimed_at: datetime | None = None


class AchievementsResponse(_StrictModel):
    catalog: list[AchievementCatalogEntryResponse]
    progress: dict[str, AchievementProgressResponse]


class GameStateResponse(_StrictModel):
    current_node_code: str | None
    ddo_profile: KlimovProfile | None
    map_locations: dict[str, MapLocationResponse]
    available_lessons: list[str]
    stage_statuses: dict[int, ContentStatus]
    completed_lesson_codes: list[str]
    unlocked_book_cards: list[str]
    task_statuses: dict[str, TaskStatus]
    dialogue_states: dict[str, DialogueStateResponse]
    task_progress: dict[str, TaskProgressResponse]
    ddo_scores: dict[str, int] | None
    ddo_dominant_codes: list[KlimovProfile]
    growth_hall: GrowthHallResponse
    content: GameContentResponse
    economy: EconomyResponse
    shop: ShopStateResponse
    lesson_results: dict[str, LessonResultResponse]
    achievements: AchievementsResponse
    first_click_seen: dict[str, bool]


class GuestSessionRequest(_StrictModel):
    event_code: str = Field(min_length=1)
    device_id: str = Field(min_length=1)


class GuestSessionResponse(_StrictModel):
    access_token: str
    token_type: Literal["bearer"]
    guest_id: str
    expires_at: datetime
    astra_chat_allowed: bool
    game_state: GameStateResponse


class AdvanceRequest(_StrictModel):
    node_code: str = Field(min_length=1)


class SceneTransitionResponse(_StrictModel):
    current_node_code: str
    unlocked_book_card_id: str | None = None


class DialogueResponse(_StrictModel):
    code: str
    text: str
    response: str
    next_code: str | None = None


class DialogueChoiceRequest(_StrictModel):
    choice_code: str = Field(min_length=1)


class InterfaceActionRequest(_StrictModel):
    action_id: str = Field(min_length=1)


class InterfaceActionResponse(_StrictModel):
    current_node_code: str
    action_state: str
    completed: bool


class KlimovSubmitRequest(_StrictModel):
    answers: dict[str, str] | None = None
    profile: KlimovProfile | None = None

    @model_validator(mode="before")
    @classmethod
    def accept_raw_answer_mapping(cls, value: Any) -> Any:
        if isinstance(value, Mapping) and set(value) == {
            str(number) for number in range(1, 21)
        }:
            return {"answers": dict(value)}
        return value

    @model_validator(mode="after")
    def require_exactly_one_submission(self) -> "KlimovSubmitRequest":
        if (self.answers is None) == (self.profile is None):
            raise ValueError("Provide exactly one of answers or profile")
        return self

    def domain_submission(self) -> dict[str, str] | str:
        if self.answers is not None:
            return self.answers
        assert self.profile is not None
        return self.profile


class KlimovResponse(GameStateResponse):
    pass


class StarkWarningResponse(_StrictModel):
    shown: bool
    text: str | None = None


class TaskAnswerResponse(_StrictModel):
    correct: bool
    hint: str | None
    help_available: bool
    status: TaskStatus | None = None
    current_node_code: str | None = None
    lesson_hints_used: int
    stark_warning: StarkWarningResponse | None = None
    solution: str | None = None
    consequence: str | None = None


class TaskHelpResponse(_StrictModel):
    status: TaskStatus
    solution: str
    consequence: str
    current_node_code: str


TaskAnswerPayload = dict[str, Any]


class ShopPurchaseRequest(_StrictModel):
    task_code: str = Field(min_length=1)


class ShopPurchaseResponse(_StrictModel):
    item_id: Literal["learning_replay", "astra_hint", "attempt_stabilizer"]
    task_code: str
    price_sircoins: int
    sircoins: int
    hint: str | None = None
    lesson_hints_used: int
    learning_node_code: str | None = None
    book_card_id: str | None = None
    effect: Literal["learning_replay", "astra_hint", "attempt_stabilizer_active"]


class FirstClickResponse(_StrictModel):
    first_click_seen: dict[str, bool]


class AchievementClaimResponse(_StrictModel):
    achievement_id: str
    status: Literal["claimed"]
    reward_sircoins: int
    sircoins: int
