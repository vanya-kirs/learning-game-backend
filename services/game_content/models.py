"""Immutable definitions for repository-backed Game content."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Literal, Mapping


DialogueMode = Literal["continue", "questions", "choice"]


def _deep_freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {key: _deep_freeze(item) for key, item in value.items()}
        )
    if isinstance(value, (list, tuple)):
        return tuple(_deep_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(_deep_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class Hint:
    level: int
    text: str
    hidden: bool = True


@dataclass(frozen=True)
class DialogueNode:
    code: str
    mode: DialogueMode
    lines: tuple[str, ...]
    questions: tuple[Mapping[str, str], ...] = ()
    choices: tuple[Mapping[str, str], ...] = ()
    continue_label: str = "Продолжить"

    def __post_init__(self) -> None:
        object.__setattr__(self, "lines", tuple(self.lines))
        object.__setattr__(self, "questions", _deep_freeze(self.questions))
        object.__setattr__(self, "choices", _deep_freeze(self.choices))


@dataclass(frozen=True)
class Lesson:
    code: str
    stage: int
    subject: str
    number: int
    title: str
    prerequisite_codes: tuple[str, ...] = ()
    dialogue_node_codes: tuple[str, ...] = ()
    task_codes: tuple[str, ...] = ()
    book_card_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "prerequisite_codes", tuple(self.prerequisite_codes))
        object.__setattr__(self, "dialogue_node_codes", tuple(self.dialogue_node_codes))
        object.__setattr__(self, "task_codes", tuple(self.task_codes))
        object.__setattr__(self, "book_card_ids", tuple(self.book_card_ids))


@dataclass(frozen=True)
class Task:
    code: str
    stage: int
    subject: str
    lesson_code: str
    number: int
    prompt: str
    input_schema: Mapping[str, Any]
    answer_key: Any
    hints: tuple[Hint, ...]
    solution: str
    book_card_id: str
    consequence: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "input_schema", _deep_freeze(self.input_schema))
        object.__setattr__(self, "answer_key", _deep_freeze(self.answer_key))
        object.__setattr__(self, "hints", tuple(self.hints))


@dataclass(frozen=True)
class BookCard:
    id: str
    stage: int
    subject: str
    lesson_code: str
    title: str
    content: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "content", tuple(self.content))
