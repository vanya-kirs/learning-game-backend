from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from services.game_content import Hint, Lesson, Task, available_lessons, public_task
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
from services import learning_game_service


def test_stage_one_has_six_lessons_and_twenty_four_tasks():
    lessons = CATALOG.stage_lessons(1)
    assert {lesson.code for lesson in lessons} == {
        "Э1-ИНФ-01", "Э1-ИНФ-02", "Э1-ИИ-01", "Э1-ИИ-02",
        "Э1-РОБ-01", "Э1-РОБ-02",
    }
    assert len({code for lesson in lessons for code in lesson.task_codes}) == 24
    assert all(len(lesson.task_codes) == 4 for lesson in lessons)


def test_pythagoras_catalog_has_four_stages_and_twenty_four_lessons():
    expected = {
        1: {
            "П1-АЛ-01", "П1-АЛ-02", "П1-ГЕ-01",
            "П1-ГЕ-02", "П1-ТВ-01", "П1-ТВ-02",
        },
        2: {
            "П2-АЛ-03", "П2-АЛ-04", "П2-ГЕ-03",
            "П2-ГЕ-04", "П2-ТВ-03", "П2-ТВ-04",
        },
        3: {
            "П3-АЛ-05", "П3-АЛ-06", "П3-ГЕ-05",
            "П3-ГЕ-06", "П3-ТВ-05", "П3-ТВ-06",
        },
        4: {
            "П4-АЛ-07", "П4-АЛ-08", "П4-ГЕ-07",
            "П4-ГЕ-08", "П4-ТВ-07", "П4-ТВ-08",
        },
    }

    for stage, lesson_codes in expected.items():
        lessons = PYTHAGORAS_CATALOG.stage_lessons(stage)
        assert {lesson.code for lesson in lessons} == lesson_codes
        assert len({code for lesson in lessons for code in lesson.task_codes}) == 24
        assert all(len(lesson.task_codes) == 4 for lesson in lessons)


def test_pythagoras_catalog_keeps_stages_subjects_and_first_lesson_details():
    assert PYTHAGORAS_CATALOG.lesson("П1-АЛ-01").title == "Сбой в первой строке"
    assert PYTHAGORAS_CATALOG.lesson("П1-АЛ-02").prerequisite_codes == ("П1-АЛ-01",)
    assert PYTHAGORAS_CATALOG.lesson("П1-ГЕ-01").title == "Углы не сходятся"
    assert PYTHAGORAS_CATALOG.lesson("П4-ТВ-08").title == "Устойчивое решение"

    task = PYTHAGORAS_CATALOG.task("П1-АЛ-01-01")
    assert task.stage == 1
    assert task.subject == "Алгебра"
    assert task.answer_key == {"answer": "23"}
    assert "Меридий" in task.prompt
    assert task.solution == "12 − 7 = 5; 3 · 5 = 15; 8 + 15 = 23."

    card = PYTHAGORAS_CATALOG.book_cards[task.book_card_id]
    assert card.lesson_code == "П1-АЛ-01"
    assert "поряд" in " ".join(card.content).casefold()


def test_chz_profile_selects_pythagoras_catalog_and_keeps_stark_as_default():
    pythagoras = learning_game_service.catalog_for_profile("chz")
    default = learning_game_service.catalog_for_profile("cht")

    assert pythagoras is PYTHAGORAS_CATALOG
    assert default is CATALOG
    assert "П1-АЛ-01" in pythagoras.lessons
    assert "Э1-ИНФ-01" in default.lessons


def test_chkh_profile_selects_mayakovsky_catalog_and_keeps_stark_as_default():
    mayakovsky = learning_game_service.catalog_for_profile("chkh")
    default = learning_game_service.catalog_for_profile("cht")

    assert mayakovsky is MAYAKOVSKY_CATALOG
    assert default is CATALOG
    assert "МАЯ-Э1-РУ-01" in mayakovsky.lessons
    assert "Э1-ИНФ-01" in default.lessons


def test_sheldon_catalog_has_four_subjects_per_stage_and_full_task_grid():
    expected_first_lessons = {
        "ШД-Э1-ФИЗ-01",
        "ШД-Э1-ХИМ-01",
        "ШД-Э1-БИО-01",
        "ШД-Э1-ГЕО-01",
    }

    assert len(SHELDON_CATALOG.lessons) == 32
    assert len(SHELDON_CATALOG.tasks) == 128
    assert len(SHELDON_CATALOG.book_cards) == 128
    assert set(SHELDON_CATALOG.available_lessons(())) == expected_first_lessons
    for stage in range(1, 5):
        lessons = SHELDON_CATALOG.stage_lessons(stage)
        assert len(lessons) == 8
        assert {lesson.subject for lesson in lessons} == {
            "Физика",
            "Химия",
            "Биология",
            "География",
        }
        assert len({code for lesson in lessons for code in lesson.task_codes}) == 32
        assert all(len(lesson.task_codes) == 4 for lesson in lessons)


def test_chp_profile_selects_sheldon_catalog_and_map_location():
    sheldon = learning_game_service.catalog_for_profile("chp")
    default = learning_game_service.catalog_for_profile("cht")
    locations = map_locations_after_klimov("chp")

    assert sheldon is SHELDON_CATALOG
    assert default is CATALOG
    assert "ШД-Э1-ФИЗ-01" in sheldon.lessons
    assert "Э1-ИНФ-01" in default.lessons
    assert locations["sheldon"]["status"] == "available"
    assert locations["sheldon"]["title"] == "Эйдосфера"


def test_chch_profile_selects_churchill_catalog_and_map_location():
    churchill = learning_game_service.catalog_for_profile("chch")
    default = learning_game_service.catalog_for_profile("cht")
    locations = map_locations_after_klimov("chch")

    assert churchill is CHURCHILL_CATALOG
    assert default is CATALOG
    assert len(churchill.lessons) == 24
    assert len(churchill.tasks) == 96
    assert "ЧЧ-Э1-ИЯ-01" in churchill.lessons
    assert "ЧЧ-Э4-ВИ-08-04" in churchill.tasks
    assert locations["churchill"]["status"] == "available"
    assert locations["churchill"]["title"] == "Конкордия"
    assert locations["churchill"]["local_astra_point"] == "Логос"
    assert locations["churchill"]["image_asset"] == "subjects/Черчилль ЧЧ/Карта/concordia-approved.png"
    assert locations["churchill"]["mentor_asset"] == "subjects/Черчилль ЧЧ/Образ/churchill-approved.png"
    assert [point["title"] for point in locations["churchill"]["map_points"]] == [
        "Логос",
        "Английская академия",
        "Палата Согласия",
        "Дом Исторических Путей",
    ]


def test_churchill_catalog_preserves_subject_sequence_and_task_shape():
    assert CHURCHILL_CATALOG.lesson("ЧЧ-Э1-ИЯ-02").prerequisite_codes == ("ЧЧ-Э1-ИЯ-01",)
    assert CHURCHILL_CATALOG.lesson("ЧЧ-Э2-ИЯ-03").prerequisite_codes == ("ЧЧ-Э1-ИЯ-02",)
    assert CHURCHILL_CATALOG.lesson("ЧЧ-Э4-ВИ-08").title == "Урок первой катастрофы"

    task = CHURCHILL_CATALOG.task("ЧЧ-Э1-ИЯ-01-01")
    assert task.stage == 1
    assert task.subject == "Иностранный язык (английский)"
    assert task.answer_key == {"answer": "1011"}
    assert "Конкордия" in task.prompt
    assert task.mini_learning
    assert [hint.level for hint in task.hints] == [1, 2, 3, 4, 5]


def test_sheldon_catalog_preserves_subject_sequence_inside_free_stage_order():
    assert SHELDON_CATALOG.lesson("ШД-Э1-ФИЗ-02").prerequisite_codes == ("ШД-Э1-ФИЗ-01",)
    assert SHELDON_CATALOG.lesson("ШД-Э2-ФИЗ-03").prerequisite_codes == ("ШД-Э1-ФИЗ-02",)
    assert SHELDON_CATALOG.lesson("ШД-Э4-ГЕО-08").title == "Путь к точке выхода"

    task = SHELDON_CATALOG.task("ШД-Э1-ФИЗ-01-01")
    assert task.stage == 1
    assert task.subject == "Физика"
    assert task.answer_key == {"answer": "111"}
    assert "Тепло уходит из купола" in task.prompt
    assert task.mini_learning
    assert [hint.level for hint in task.hints] == [1, 2, 3, 4, 5]


def test_stage_two_has_six_lessons_and_twenty_four_tasks():
    lessons = CATALOG.stage_lessons(2)
    assert {lesson.code for lesson in lessons} == {
        "Э2-ИНФ-03", "Э2-ИНФ-04", "Э2-ИИ-03", "Э2-ИИ-04",
        "Э2-РОБ-03", "Э2-РОБ-04",
    }
    assert len({code for lesson in lessons for code in lesson.task_codes}) == 24
    assert all(len(lesson.task_codes) == 4 for lesson in lessons)


def test_stage_three_and_four_have_six_lessons_and_twenty_four_tasks_each():
    assert {lesson.code for lesson in CATALOG.stage_lessons(3)} == {
        "Э3-ИНФ-05", "Э3-ИНФ-06", "Э3-ИИ-05", "Э3-ИИ-06",
        "Э3-РОБ-05", "Э3-РОБ-06",
    }
    assert {lesson.code for lesson in CATALOG.stage_lessons(4)} == {
        "Э4-ИНФ-07", "Э4-ИНФ-08", "Э4-ИИ-07", "Э4-ИИ-08",
        "Э4-РОБ-07", "Э4-РОБ-08",
    }
    for stage in (3, 4):
        lessons = CATALOG.stage_lessons(stage)
        assert len({code for lesson in lessons for code in lesson.task_codes}) == 24
        assert all(len(lesson.task_codes) == 4 for lesson in lessons)


def test_stages_unlock_after_previous_stage_is_completed():
    assert CATALOG.stage_status(2, completed_lessons=set()) == "locked"
    assert CATALOG.stage_status(
        2,
        completed_lessons=set(CATALOG.stage_lesson_codes(1)),
    ) == "available"
    assert CATALOG.stage_status(3, completed_lessons=set()) == "locked"
    assert CATALOG.stage_status(
        3,
        completed_lessons=set(
            CATALOG.stage_lesson_codes(1) + CATALOG.stage_lesson_codes(2)
        ),
    ) == "available"
    assert CATALOG.stage_status(
        4,
        completed_lessons=set(
            CATALOG.stage_lesson_codes(1)
            + CATALOG.stage_lesson_codes(2)
            + CATALOG.stage_lesson_codes(3)
        ),
    ) == "available"
    assert CATALOG.stage_status(
        5,
        completed_lessons=set(
            CATALOG.stage_lesson_codes(1)
            + CATALOG.stage_lesson_codes(2)
            + CATALOG.stage_lesson_codes(3)
            + CATALOG.stage_lesson_codes(4)
        ),
    ) == "soon"


def test_stage_two_subjects_can_start_in_any_order_then_require_the_first_lesson():
    completed_stage_one = set(CATALOG.stage_lesson_codes(1))
    assert {
        "Э2-ИНФ-03", "Э2-ИИ-03", "Э2-РОБ-03",
    }.issubset(available_lessons(completed_stage_one))
    for subject in ("ИНФ", "ИИ", "РОБ"):
        first = f"Э2-{subject}-03"
        second = f"Э2-{subject}-04"
        assert CATALOG.lesson(second).prerequisite_codes == (first,)
        assert second not in available_lessons(completed_stage_one)
        assert second in available_lessons({*completed_stage_one, first})


def test_stage_three_and_four_subjects_can_start_after_previous_stage_then_require_first_lesson():
    stage_two_completed = set(CATALOG.stage_lesson_codes(1) + CATALOG.stage_lesson_codes(2))
    assert {
        "Э3-ИНФ-05", "Э3-ИИ-05", "Э3-РОБ-05",
    }.issubset(available_lessons(stage_two_completed))
    for subject in ("ИНФ", "ИИ", "РОБ"):
        first = f"Э3-{subject}-05"
        second = f"Э3-{subject}-06"
        assert CATALOG.lesson(second).prerequisite_codes == (first,)
        assert second not in available_lessons(stage_two_completed)
        assert second in available_lessons({*stage_two_completed, first})

    stage_three_completed = set(
        CATALOG.stage_lesson_codes(1)
        + CATALOG.stage_lesson_codes(2)
        + CATALOG.stage_lesson_codes(3)
    )
    assert {
        "Э4-ИНФ-07", "Э4-ИИ-07", "Э4-РОБ-07",
    }.issubset(available_lessons(stage_three_completed))
    for subject in ("ИНФ", "ИИ", "РОБ"):
        first = f"Э4-{subject}-07"
        second = f"Э4-{subject}-08"
        assert CATALOG.lesson(second).prerequisite_codes == (first,)
        assert second not in available_lessons(stage_three_completed)
        assert second in available_lessons({*stage_three_completed, first})


def test_stage_two_tasks_keep_private_solution_material_and_complete_cards():
    for lesson in CATALOG.stage_lessons(2):
        for code in lesson.task_codes:
            task = CATALOG.task(code)
            assert [hint.level for hint in task.hints] == [1, 2, 3, 4, 5]
            assert len({hint.text for hint in task.hints}) == 5
            assert all(hint.hidden for hint in task.hints)
            assert public_task(code)["hints"] == ()
            assert task.answer_key and task.solution
            assert task.mini_learning
            card = CATALOG.book_cards[task.book_card_id]
            assert card.lesson_code == lesson.code
            assert card.content and all(part.strip() for part in card.content)
            assert task.solution not in public_task(code)["prompt"]




def test_stage_two_public_schemas_do_not_reveal_a_single_correct_answer():
    for lesson in CATALOG.stage_lessons(2):
        for code in lesson.task_codes:
            task = CATALOG.task(code)
            schema = public_task(code)["input_schema"]
            for field, field_schema in schema["properties"].items():
                assert "const" not in field_schema
                assert field_schema.get("type") != "null"
                if "enum" in field_schema:
                    assert len(field_schema["enum"]) > 1
                    assert field_schema["enum"] != [task.answer_key[field]]

    for code in ("Э2-ИНФ-04-04", "Э2-РОБ-04-04"):
        selected = public_task(code)["input_schema"]["properties"]["selected"]
        assert selected["type"] == ["string", "null"]
        assert None in selected["enum"]
        assert len(selected["enum"]) == 3


def test_stage_two_book_cards_preserve_independent_validation_requirements():
    model_card = CATALOG.book_cards["Э2-ИИ-03-04-КНИЖКА"]
    learning_card = CATALOG.book_cards["Э2-ИИ-04-04-КНИЖКА"]

    assert "независим" in " ".join(model_card.content).casefold()
    assert "независим" in " ".join(learning_card.content).casefold()
    assert "провер" in " ".join(model_card.content).casefold()
    assert "mae" in " ".join(learning_card.content).casefold()


def test_stage_two_scenes_gate_tasks_and_keep_questions_optional():
    assert CATALOG.dialogue_nodes["Э2-ВХОД-В"].required_lesson_codes == (
        "Э1-ИНФ-01", "Э1-ИНФ-02", "Э1-ИИ-01",
        "Э1-ИИ-02", "Э1-РОБ-01", "Э1-РОБ-02",
    )
    assert CATALOG.dialogue_nodes["Э2-ФИНАЛ"].next_code == "stage_hub"

    for lesson in CATALOG.stage_lessons(2):
        menu = CATALOG.dialogue_nodes[f"{lesson.code}-В"]
        assert menu.mode == "questions"
        assert len(menu.questions) == 3
        assert all(item["next_code"] == menu.code for item in menu.questions)
        for code in lesson.dialogue_node_codes:
            node = CATALOG.dialogue_nodes[code]
            assert node.next_code in {*CATALOG.dialogue_nodes, *CATALOG.tasks, "stage_hub"}
            if node.phase == "consequence":
                assert node.task_code in node.required_task_codes
            if node.phase == "completion":
                assert node.required_task_codes == lesson.task_codes
            if node.mode == "choice":
                assert len(node.choices) in (3, 4)
                assert all(item["next_code"] == node.next_code for item in node.choices)
                assert all(item["text"] not in node.lines for item in node.choices)


@pytest.mark.parametrize(("code", "expected"), [
    ("Э2-ИНФ-03-01", {"fields_bytes": 28, "service_bytes": 2, "total_bytes": 30}),
    ("Э2-ИНФ-03-02", {"records_bytes": 7200, "header_bytes": 800, "total_bytes": 8000, "total_kb": 8}),
    ("Э2-ИНФ-03-03", {"compressed_bytes": 5200, "saved_bytes": 2800}),
    ("Э2-ИНФ-03-04", {"required_kb": 16, "a_margin_kb": -1, "b_margin_kb": 2, "selected": "Б"}),
    ("Э2-ИНФ-04-01", {"time_s": 6}),
    ("Э2-ИНФ-04-02", {"packet_count": 3}),
    ("Э2-ИНФ-04-03", {"total_kb": 8.6, "time_s": 2.87}),
    ("Э2-ИНФ-04-04", {"a_time_s": 3.87, "b_time_s": 4.5, "window_s": 3.5, "a_passes": False, "b_passes": False, "selected": None}),
    ("Э2-ИИ-03-01", {"contribution": 6}),
    ("Э2-ИИ-03-02", {"first_contribution": 6, "second_contribution": 4, "score": 8}),
    ("Э2-ИИ-03-03", {"a_suitable": True, "b_suitable": False}),
    ("Э2-ИИ-03-04", {"a_accuracy_percent": 80, "b_accuracy_percent": 87.5, "a_dangerous_errors": 1, "b_dangerous_errors": 0, "selected": "Б"}),
    ("Э2-ИИ-04-01", {"error_minutes": 3, "direction": "завышение"}),
    ("Э2-ИИ-04-02", {"absolute_errors": (3, 1, 2), "mae_minutes": 2}),
    ("Э2-ИИ-04-03", {"correction": 1, "new_bias": 4}),
    ("Э2-ИИ-04-04", {"k_0_5_mae_minutes": 1.2, "k_1_mae_minutes": 1.8, "selected_k": 0.5}),
    ("Э2-РОБ-03-01", {"offset_m": 0.3}),
    ("Э2-РОБ-03-02", {"sum_m": 0.9, "average_m": 0.3}),
    ("Э2-РОБ-03-03", {"corrected_m": 5.9}),
    ("Э2-РОБ-03-04", {"errors_m": (0.1, 0.1, 0.2), "tolerance_m": 0.15, "passes": False}),
    ("Э2-РОБ-04-01", {"error_cm": 4}),
    ("Э2-РОБ-04-02", {"correction_cm": 2}),
    ("Э2-РОБ-04-03", {"new_position_cm": 16, "remaining_error_cm": 2}),
    ("Э2-РОБ-04-04", {"k_0_5_positions_cm": (16, 18), "k_0_5_final_error_cm": 2, "k_0_5_overshoot": False, "k_1_5_positions_cm": (24, 18), "k_1_5_final_error_cm": 2, "k_1_5_overshoot": True, "selected": None}),
])
def test_all_stage_two_hard_keys_preserve_source_calculations_and_decisions(code, expected):
    assert dict(CATALOG.task(code).answer_key) == expected


def test_stage_one_subjects_can_start_in_any_order():
    assert set(available_lessons(set())) == {"Э1-ИНФ-01", "Э1-ИИ-01", "Э1-РОБ-01"}
    for subject in ("ИНФ", "ИИ", "РОБ"):
        first = f"Э1-{subject}-01"
        second = f"Э1-{subject}-02"
        assert CATALOG.lesson(second).prerequisite_codes == (first,)
        assert second in available_lessons({first})


def test_stage_one_tasks_keep_five_private_hints_and_complete_learning_cards():
    for lesson in CATALOG.stage_lessons(1):
        for code in lesson.task_codes:
            task = CATALOG.task(code)
            assert [hint.level for hint in task.hints] == [1, 2, 3, 4, 5]
            assert len({hint.text for hint in task.hints}) == 5
            assert all(hint.hidden for hint in task.hints)
            assert public_task(code)["hints"] == ()
            assert task.solution and task.consequence and task.answer_key
            card = CATALOG.book_cards[task.book_card_id]
            assert card.lesson_code == lesson.code
            assert task.mini_learning
            assert card.content and all(part.strip() for part in card.content)
            assert task.solution not in public_task(code)["prompt"]


def test_stark_player_facing_text_excludes_editorial_instructions():
    editorial_markers = (
        "не утверждать",
        "не утверждает",
        "не произносить",
        "не раскрывать",
        "предложенная постановка",
        "при будущем утверждении",
        "после мини-обучения",
        "после обучения в книжку",
        "в карточку включить",
        "самостоятельный ответ не добавлять",
        "для автора",
        "требуют адаптации",
        "не переписывается",
        "сюжетные сведения",
        "не скрытые исходные данные",
        "не дополнительная задача",
        "по общему сценарию",
        "при любом порядке занятий",
        "доступно независимо",
        "не требует завершения других предметов",
        "автономный контрольный пример",
        "отдельное указанное событие",
        "не следствие оценки",
        "ответ для автора",
        "статус: подробный сценарный черновик",
        "не симулируется",
        "в сюжет не переносится",
        "между этапами",
        "результат i3",
        "результат i4",
        "результат a3",
        "результат a4",
        "результат r3",
        "результат r4",
        "расчёт времени передачи сохранён",
        "число пакетов сохранено",
        "полный объём и время передачи сохранены",
        "вклад признака рассчитан",
        "линейная оценка рассчитана",
        "ошибка прогноза измерена",
        "средняя абсолютная ошибка рассчитана",
        "новое смещение рассчитано",
        "смещение датчика измерено",
        "среднее смещение серии рассчитано",
        "исправленное показание рассчитано",
        "отклонение от цели рассчитано",
        "корректировка положения рассчитана",
        "новый шаг и оставшаяся ошибка рассчитаны",
    )
    player_facing_text = []

    for lesson in (*CATALOG.stage_lessons(1), *CATALOG.stage_lessons(2)):
        player_facing_text.extend((lesson.subject, lesson.title))
        for code in lesson.task_codes:
            task = CATALOG.task(code)
            player_facing_text.extend((
                task.prompt,
                task.solution,
                task.consequence,
                task.mini_learning,
                *(hint.text for hint in task.hints),
            ))
        for card_id in lesson.book_card_ids:
            card = CATALOG.book_cards[card_id]
            player_facing_text.extend((card.title, *card.content))
        for code in lesson.dialogue_node_codes:
            node = CATALOG.dialogue_nodes[code]
            player_facing_text.extend((*node.lines, node.continue_label))
            for item in (*node.questions, *node.choices):
                player_facing_text.extend(
                    value for key, value in item.items()
                    if key in {"text", "response"}
                )

    leaks = {
        marker: text
        for text in player_facing_text
        for marker in editorial_markers
        if marker.casefold() in text.casefold()
    }
    assert leaks == {}


def test_stage_one_scenes_gate_consequences_and_keep_questions_optional():
    for lesson in CATALOG.stage_lessons(1):
        menu = CATALOG.dialogue_nodes[f"{lesson.code}-В"]
        assert menu.mode == "questions"
        assert len(menu.questions) == 3
        assert menu.continue_label == "Перейти к проверке"
        assert all(item["next_code"] == menu.code for item in menu.questions)
        for code in lesson.dialogue_node_codes:
            node = CATALOG.dialogue_nodes[code]
            assert node.next_code in {*CATALOG.dialogue_nodes, *CATALOG.tasks, "stage_hub"}
            if node.phase == "consequence":
                assert node.task_code in node.required_task_codes
            if node.phase == "completion":
                assert node.required_task_codes == lesson.task_codes
            if node.mode == "choice":
                assert len(node.choices) in (3, 4)
                assert all(item["next_code"] == node.next_code for item in node.choices)
                assert all(item["text"] not in node.lines for item in node.choices)


@pytest.mark.parametrize(("code", "expected"), [
    ("Э1-ИНФ-02-04", {"sums": (23, 33), "checksums": (3, 3), "weighted_checksums": (38, 48), "selected": "А", "blocked": "Б"}),
    ("Э1-ИИ-01-04", {"planned": 80, "usable": 56, "shortfall": 4, "complete": False}),
    ("Э1-ИИ-02-02", {"initial_percent": 25, "remaining": 2, "remaining_percent": 10, "all_checked": False}),
    ("Э1-РОБ-01-04", {"masses_kg": (40, 41, 44), "times_h": (1.5, 2, 3), "selected": "Б", "mass_margin_kg": 1}),
    ("Э1-РОБ-02-04", {"max_interval_s": 0.3, "min_frequency_hz": "10/3", "required_distances_m": (2.8, 2.2, 2), "selected": "Б"}),
])
def test_stage_one_hard_keys_preserve_combined_calculations_and_decisions(code, expected):
    assert dict(CATALOG.task(code).answer_key) == expected


def test_public_task_never_contains_private_solution_data():
    payload = public_task("Э1-ИНФ-01-01")

    assert "answer_key" not in payload
    assert "solution" not in payload
    assert "consequence" not in payload


def test_public_task_uses_an_explicit_safe_field_set():
    payload = public_task("Э1-ИНФ-01-01")

    assert set(payload) == {
        "code",
        "stage",
        "subject",
        "lesson_code",
        "number",
        "prompt",
        "input_schema",
        "hints",
        "book_card_id",
    }


def test_public_task_omits_hidden_hint_levels():
    payload = public_task("Э1-ИНФ-01-01")

    assert payload["hints"] == ()


def test_second_lesson_requires_first():
    assert "Э1-ИНФ-02" not in available_lessons(set())
    assert "Э1-ИНФ-02" in available_lessons({"Э1-ИНФ-01"})


def test_content_models_are_frozen():
    hint = Hint(level=1, text="Подсказка")

    with pytest.raises(FrozenInstanceError):
        hint.text = "Изменена"


def test_task_nested_content_is_deeply_frozen():
    task = CATALOG.task("Э1-ИНФ-01-01")

    with pytest.raises(TypeError):
        task.input_schema["properties"]["sum"]["type"] = "string"
    with pytest.raises(TypeError):
        task.answer_key["sum"] = 23
    with pytest.raises(AttributeError):
        task.answer_key["place_values"].append(1)


def test_catalog_indexes_tasks_by_code():
    assert CATALOG.task("Э1-ИНФ-01-01").lesson_code == "Э1-ИНФ-01"
    assert "двоичный-адрес" in CATALOG.book_cards


def test_catalog_rejects_dangling_task_book_card_reference():
    lesson = Lesson(
        code="Э1-ТЕСТ-01",
        stage=1,
        subject="Тест",
        number=1,
        title="Тест",
        task_codes=("Э1-ТЕСТ-01-01",),
    )
    task = Task(
        code="Э1-ТЕСТ-01-01",
        stage=1,
        subject="Тест",
        lesson_code=lesson.code,
        number=1,
        prompt="Тест",
        input_schema={},
        answer_key={},
        hints=(),
        solution="Тест",
        book_card_id="missing-card",
        consequence="Тест",
    )

    with pytest.raises(ValueError, match="missing-card"):
        ContentCatalog.build(lessons=(lesson,), tasks=(task,))


def test_unknown_task_is_not_projected():
    with pytest.raises(KeyError):
        public_task("неизвестная-задача")


def test_map_opens_active_branch_for_ready_klimov_profiles():
    expected_available = {
        "chp": "sheldon",
        "cht": "stark_indaris",
        "chch": "churchill",
        "chz": "pythagoras",
        "chkh": "mayakovsky",
    }

    for profile, active_location in expected_available.items():
        locations = map_locations_after_klimov(profile)

        assert locations[active_location]["status"] == "available"
        for code, location in locations.items():
            if code != active_location:
                assert location["status"] == "soon"


def test_onboarding_uses_approved_dialogue_modes_and_ddo_gate():
    nodes = {node.code: node for node in ONBOARDING_NODES}

    assert tuple(nodes) == (
        "ПР-01",
        "ПР-Д01",
        "ПР-02",
        "ПР-03",
        "ПР-Д02",
        "ПР-04",
        "ПР-05",
        "ПР-06",
        "ПР-07",
    )
    assert nodes["ПР-01"].mode == "choice"
    assert len(nodes["ПР-01"].choices) == 3
    assert nodes["ПР-02"].mode == "questions"
    assert len(nodes["ПР-02"].questions) == 3
    assert nodes[DDO_NODE_CODE].continue_label == "Открыть опросник"
    assert DDO_NODE_CODE in CATALOG.dialogue_nodes


def test_digital_book_must_be_opened_and_returned_before_ddo():
    nodes = {node.code: node for node in ONBOARDING_NODES}
    book = nodes["ПР-Д02"]

    state = book.apply_action(book.initial_state, "open_knowledge_book")
    assert book.is_complete(state) is False

    state = book.apply_action(state, "return_from_knowledge_book")
    assert book.is_complete(state) is True


def test_panel_requires_three_interface_actions_and_rejects_generic_continue():
    nodes = {node.code: node for node in ONBOARDING_NODES}
    panel = nodes["ПР-Д01"]

    assert panel.mode == "action"
    assert panel.action_ids == (
        "open_highlighted_panel",
        "select_backup_channel",
        "confirm_connection",
    )
    assert all(action.instruction for action in panel.actions)

    with pytest.raises(ValueError, match="Unknown action"):
        panel.apply_action(panel.initial_state, "continue")

    state = panel.initial_state
    for action_id in panel.action_ids:
        state = panel.apply_action(state, action_id)
    assert panel.is_complete(state) is True


def test_map_starts_with_five_soon_cards_and_preserves_profile_labels():
    assert len(MAP_LOCATIONS) == 5
    assert {location["status"] for location in MAP_LOCATIONS.values()} == {"soon"}
    assert {location["profile"] for location in MAP_LOCATIONS.values()} == {
        "chp",
        "cht",
        "chch",
        "chz",
        "chkh",
    }


def test_stark_choice_hands_off_through_the_compass_for_every_response():
    node = CATALOG.dialogue_nodes["ПР-07"]

    assert all(
        "АСТРА: «Переход подготовлен" in choice["response"]
        for choice in node.choices
    )
