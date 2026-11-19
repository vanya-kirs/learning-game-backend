"""Indexes and safe projections for Game's server-owned content."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from .models import BookCard, DialogueNode, Lesson, Task
from .churchill import (
    CHURCHILL_BOOK_CARDS,
    CHURCHILL_DIALOGUE_NODES,
    CHURCHILL_LESSONS,
    CHURCHILL_TASKS,
)
from .mayakovsky import (
    MAYAKOVSKY_BOOK_CARDS,
    MAYAKOVSKY_DIALOGUE_NODES,
    MAYAKOVSKY_LESSONS,
    MAYAKOVSKY_TASKS,
)
from .onboarding import ONBOARDING_NODES
from .pythagoras import (
    PYTHAGORAS_BOOK_CARDS,
    PYTHAGORAS_DIALOGUE_NODES,
    PYTHAGORAS_LESSONS,
    PYTHAGORAS_TASKS,
)
from .sheldon import (
    SHELDON_BOOK_CARDS,
    SHELDON_DIALOGUE_NODES,
    SHELDON_LESSONS,
    SHELDON_TASKS,
)
from .stark_stage_1 import (
    STAGE_ONE_BOOK_CARDS,
    STAGE_ONE_DIALOGUE_NODES,
    STAGE_ONE_LESSONS,
    STAGE_ONE_TASKS,
)
from .stark_stage_2 import (
    STAGE_TWO_BOOK_CARDS,
    STAGE_TWO_DIALOGUE_NODES,
    STAGE_TWO_LESSONS,
    STAGE_TWO_TASKS,
)
from .stark_stage_3 import (
    STAGE_THREE_BOOK_CARDS,
    STAGE_THREE_DIALOGUE_NODES,
    STAGE_THREE_LESSONS,
    STAGE_THREE_TASKS,
)
from .stark_stage_4 import (
    STAGE_FOUR_BOOK_CARDS,
    STAGE_FOUR_DIALOGUE_NODES,
    STAGE_FOUR_LESSONS,
    STAGE_FOUR_TASKS,
)


_PUBLIC_TASK_FIELDS = (
    "code",
    "stage",
    "subject",
    "lesson_code",
    "number",
    "prompt",
    "input_schema",
    "hints",
    "book_card_id",
)
_IGNORED_ANSWER_FIELDS = frozenset(("calculation", "justification", "apply"))


def _unique_index(items: Iterable[Any], attribute: str) -> Mapping[str, Any]:
    index: dict[str, Any] = {}
    for item in items:
        key = getattr(item, attribute)
        if key in index:
            raise ValueError(f"Duplicate Game content identifier: {key}")
        index[key] = item
    return MappingProxyType(index)


def _deep_thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _deep_thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_deep_thaw(item) for item in value]
    if isinstance(value, frozenset):
        return [_deep_thaw(item) for item in value]
    return value


def public_answer_schema(task: Task) -> dict[str, Any]:
    schema = _deep_thaw(task.input_schema)
    answer_keys = set(task.answer_key) if isinstance(task.answer_key, Mapping) else set()
    if schema.get("type") != "object" or not answer_keys:
        return schema
    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        return schema
    allowed = answer_keys - _IGNORED_ANSWER_FIELDS
    schema["properties"] = {
        key: value
        for key, value in properties.items()
        if key in allowed
    }
    schema["required"] = [
        key for key in schema.get("required", ())
        if key in schema["properties"]
    ]
    return schema


def _require_reference(
    source: str,
    target: str,
    index: Mapping[str, Any],
    kind: str,
) -> None:
    if target not in index:
        raise ValueError(f"{source} references missing {kind}: {target}")


@dataclass(frozen=True)
class ContentCatalog:
    lessons: Mapping[str, Lesson]
    tasks: Mapping[str, Task]
    dialogue_nodes: Mapping[str, DialogueNode]
    book_cards: Mapping[str, BookCard]

    @classmethod
    def build(
        cls,
        *,
        lessons: Iterable[Lesson] = (),
        tasks: Iterable[Task] = (),
        dialogue_nodes: Iterable[DialogueNode] = (),
        book_cards: Iterable[BookCard] = (),
    ) -> "ContentCatalog":
        lesson_index = _unique_index(lessons, "code")
        task_index = _unique_index(tasks, "code")
        dialogue_index = _unique_index(dialogue_nodes, "code")
        book_card_index = _unique_index(book_cards, "id")

        for lesson in lesson_index.values():
            for prerequisite_code in lesson.prerequisite_codes:
                _require_reference(
                    lesson.code, prerequisite_code, lesson_index, "lesson"
                )
            for task_code in lesson.task_codes:
                _require_reference(lesson.code, task_code, task_index, "task")
            for node_code in lesson.dialogue_node_codes:
                _require_reference(
                    lesson.code, node_code, dialogue_index, "dialogue node"
                )
            for book_card_id in lesson.book_card_ids:
                _require_reference(
                    lesson.code, book_card_id, book_card_index, "book card"
                )

        for task in task_index.values():
            _require_reference(task.code, task.lesson_code, lesson_index, "lesson")
            if task.book_card_id:
                _require_reference(
                    task.code, task.book_card_id, book_card_index, "book card"
                )

        for book_card in book_card_index.values():
            _require_reference(
                book_card.id, book_card.lesson_code, lesson_index, "lesson"
            )

        return cls(
            lessons=lesson_index,
            tasks=task_index,
            dialogue_nodes=dialogue_index,
            book_cards=book_card_index,
        )

    def task(self, task_code: str) -> Task:
        return self.tasks[task_code]

    def lesson(self, lesson_code: str) -> Lesson:
        return self.lessons[lesson_code]

    def stage_lessons(self, stage: int) -> tuple[Lesson, ...]:
        return tuple(
            lesson
            for lesson in self.lessons.values()
            if lesson.stage == stage
        )

    def stage_lesson_codes(self, stage: int) -> tuple[str, ...]:
        return tuple(lesson.code for lesson in self.stage_lessons(stage))

    def available_lessons(self, completed_codes: Iterable[str]) -> tuple[str, ...]:
        completed = frozenset(completed_codes)
        return tuple(
            lesson.code
            for lesson in self.lessons.values()
            if self.stage_status(lesson.stage, completed_lessons=completed) == "available"
            and set(lesson.prerequisite_codes).issubset(completed)
        )

    def stage_status(
        self,
        stage: int,
        *,
        completed_lessons: Iterable[str],
    ) -> str:
        completed = frozenset(completed_lessons)
        if stage == 1:
            return "available"
        if stage == 2:
            required = frozenset(self.stage_lesson_codes(1))
            return "available" if required.issubset(completed) else "locked"
        if stage == 3:
            required = frozenset(self.stage_lesson_codes(2))
            return "available" if required.issubset(completed) else "locked"
        if stage == 4:
            required = frozenset(self.stage_lesson_codes(3))
            return "available" if required.issubset(completed) else "locked"
        return "soon"

    def public_task(self, task_code: str) -> dict[str, Any]:
        task = self.task(task_code)
        values = {
            "code": task.code,
            "stage": task.stage,
            "subject": task.subject,
            "lesson_code": task.lesson_code,
            "number": task.number,
            "prompt": task.prompt,
            "input_schema": public_answer_schema(task),
            "hints": tuple(
                {"level": hint.level, "text": hint.text}
                for hint in task.hints
                if not hint.hidden
            ),
            "book_card_id": task.book_card_id,
        }
        return {field: values[field] for field in _PUBLIC_TASK_FIELDS}


CATALOG = ContentCatalog.build(
    lessons=(
        *STAGE_ONE_LESSONS,
        *STAGE_TWO_LESSONS,
        *STAGE_THREE_LESSONS,
        *STAGE_FOUR_LESSONS,
    ),
    tasks=(
        *STAGE_ONE_TASKS,
        *STAGE_TWO_TASKS,
        *STAGE_THREE_TASKS,
        *STAGE_FOUR_TASKS,
    ),
    dialogue_nodes=(
        *ONBOARDING_NODES,
        *STAGE_ONE_DIALOGUE_NODES,
        *STAGE_TWO_DIALOGUE_NODES,
        *STAGE_THREE_DIALOGUE_NODES,
        *STAGE_FOUR_DIALOGUE_NODES,
    ),
    book_cards=(
        *STAGE_ONE_BOOK_CARDS,
        *STAGE_TWO_BOOK_CARDS,
        *STAGE_THREE_BOOK_CARDS,
        *STAGE_FOUR_BOOK_CARDS,
    ),
)


PYTHAGORAS_CATALOG = ContentCatalog.build(
    lessons=PYTHAGORAS_LESSONS,
    tasks=PYTHAGORAS_TASKS,
    dialogue_nodes=(
        *ONBOARDING_NODES,
        *PYTHAGORAS_DIALOGUE_NODES,
    ),
    book_cards=PYTHAGORAS_BOOK_CARDS,
)


MAYAKOVSKY_CATALOG = ContentCatalog.build(
    lessons=MAYAKOVSKY_LESSONS,
    tasks=MAYAKOVSKY_TASKS,
    dialogue_nodes=(
        *ONBOARDING_NODES,
        *MAYAKOVSKY_DIALOGUE_NODES,
    ),
    book_cards=MAYAKOVSKY_BOOK_CARDS,
)


SHELDON_CATALOG = ContentCatalog.build(
    lessons=SHELDON_LESSONS,
    tasks=SHELDON_TASKS,
    dialogue_nodes=(
        *ONBOARDING_NODES,
        *SHELDON_DIALOGUE_NODES,
    ),
    book_cards=SHELDON_BOOK_CARDS,
)


CHURCHILL_CATALOG = ContentCatalog.build(
    lessons=CHURCHILL_LESSONS,
    tasks=CHURCHILL_TASKS,
    dialogue_nodes=(
        *ONBOARDING_NODES,
        *CHURCHILL_DIALOGUE_NODES,
    ),
    book_cards=CHURCHILL_BOOK_CARDS,
)


def public_task(task_code: str) -> dict[str, Any]:
    return CATALOG.public_task(task_code)


def available_lessons(completed_codes: Iterable[str]) -> tuple[str, ...]:
    return CATALOG.available_lessons(completed_codes)
