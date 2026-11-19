"""Pythagoras branch content for Orbis.

The branch is kept in a separate catalog from Stark/Indaris until the game
service has explicit branch selection. Codes use the P-prefix to avoid mixing
progress with the existing E-stage lessons.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import BookCard, Hint, Lesson
from .stark_stage_1 import StageDialogueNode, StageTask


@dataclass(frozen=True)
class _LessonSpec:
    code: str
    stage: int
    subject: str
    number: int
    title: str
    theme: str
    card_title: str
    card_content: tuple[str, ...]
    first_prompt: str
    first_answer: str
    first_solution: str
    first_consequence: str


_LESSON_SPECS: tuple[_LessonSpec, ...] = (
    _LessonSpec(
        code="П1-АЛ-01",
        stage=1,
        subject="Алгебра",
        number=1,
        title="Сбой в первой строке",
        theme="порядок действий и числовые выражения",
        card_title="Порядок действий",
        card_content=(
            "Сначала выполняй действия в скобках, затем умножение и деление, затем сложение и вычитание.",
            "Если строка Меридия спорит сама с собой, проверь порядок действий до поиска сложной причины.",
        ),
        first_prompt="Меридий проверяет первую строку расчёта: 8 + 3 · (12 − 7). Найди верный результат.",
        first_answer="23",
        first_solution="12 − 7 = 5; 3 · 5 = 15; 8 + 15 = 23.",
        first_consequence="Первая строка Меридия стабилизирована, луч перестаёт мигать рывками.",
    ),
    _LessonSpec(
        code="П1-АЛ-02",
        stage=1,
        subject="Алгебра",
        number=2,
        title="Неизвестная в луче",
        theme="линейные уравнения",
        card_title="Линейное уравнение",
        card_content=(
            "Неизвестное можно найти обратными действиями, сохраняя равенство обеих частей.",
            "Луч Меридия принимает только то значение, которое делает обе стороны равными.",
        ),
        first_prompt="В луче Меридия записано уравнение 3x + 5 = 26. Найди x.",
        first_answer="7",
        first_solution="3x = 26 − 5 = 21; x = 21 : 3 = 7.",
        first_consequence="Луч принимает ровную высоту, и Башня Неизвестных открывает второй вход.",
    ),
    _LessonSpec(
        code="П1-ГЕ-01",
        stage=1,
        subject="Геометрия",
        number=1,
        title="Углы не сходятся",
        theme="углы при пересечении прямых",
        card_title="Смежные и вертикальные углы",
        card_content=(
            "Смежные углы дают 180 градусов. Вертикальные углы равны.",
            "Если линии на плите Орбиса разъехались, начни с пары углов, которую можно проверить.",
        ),
        first_prompt="На плите Меридия смежные углы. Один равен 68°. Найди второй.",
        first_answer="112",
        first_solution="180° − 68° = 112°.",
        first_consequence="Одна дуга Купола Построений возвращается на место.",
    ),
    _LessonSpec(
        code="П1-ГЕ-02",
        stage=1,
        subject="Геометрия",
        number=2,
        title="Площадь под куполом",
        theme="площадь прямоугольника, треугольника и составных фигур",
        card_title="Площадь фигуры",
        card_content=(
            "Сложную область можно разбить на простые части и сложить их площади.",
            "Площадь треугольника равна половине произведения основания на высоту.",
        ),
        first_prompt="Под куполом прямоугольная площадка 9 на 6 клеток. Сколько клеток занимает площадка?",
        first_answer="54",
        first_solution="9 · 6 = 54.",
        first_consequence="Плита под куполом перестаёт проваливаться у края.",
    ),
    _LessonSpec(
        code="П1-ТВ-01",
        stage=1,
        subject="Теория вероятностей",
        number=1,
        title="Случайный или сломанный",
        theme="частота события",
        card_title="Частота события",
        card_content=(
            "Частота показывает, какая доля испытаний дала нужный исход.",
            "Одна странная вспышка ещё не доказывает поломку, но серия вспышек уже даёт след.",
        ),
        first_prompt="Датчик дал 6 синих вспышек за 20 проверок. Найди частоту синих вспышек в процентах.",
        first_answer="30",
        first_solution="6 : 20 = 0,3 = 30%.",
        first_consequence="Павильон Исходов отличает случайный шум от устойчивого следа.",
    ),
    _LessonSpec(
        code="П1-ТВ-02",
        stage=1,
        subject="Теория вероятностей",
        number=2,
        title="Первый прогноз",
        theme="классическая вероятность",
        card_title="Вероятность равновозможных исходов",
        card_content=(
            "Вероятность равна числу подходящих исходов, делённому на число всех равновозможных исходов.",
            "Прогноз Орбиса не угадывает будущее, а считает долю подходящих вариантов.",
        ),
        first_prompt="В круге 8 равных секторов, 3 из них синие. Найди вероятность попасть в синий сектор в процентах.",
        first_answer="37.5",
        first_solution="3 : 8 = 0,375 = 37,5%.",
        first_consequence="Первый прогноз даёт устойчивую линию к Меридию.",
    ),
    _LessonSpec(
        code="П2-АЛ-03",
        stage=2,
        subject="Алгебра",
        number=3,
        title="Пропорции площади",
        theme="отношения и пропорции",
        card_title="Пропорция",
        card_content=("В пропорции равны отношения. Неизвестное удобно находить через крест-накрест.",),
        first_prompt="Для настройки Башни 4 кристалла питают 10 плит. Сколько плит поддержат 6 таких кристаллов?",
        first_answer="15",
        first_solution="10 : 4 = 2,5; 2,5 · 6 = 15.",
        first_consequence="Башня Неизвестных выравнивает питание второго кольца.",
    ),
    _LessonSpec(
        code="П2-АЛ-04",
        stage=2,
        subject="Алгебра",
        number=4,
        title="Две линии, две неизвестные",
        theme="системы линейных уравнений",
        card_title="Система уравнений",
        card_content=("Система ищет значения, которые одновременно подходят всем уравнениям.",),
        first_prompt="Две линии Меридия заданы системой: x + y = 11 и x − y = 3. Найди x.",
        first_answer="7",
        first_solution="Сложим уравнения: 2x = 14; x = 7.",
        first_consequence="Две линии сходятся в одной точке, не споря друг с другом.",
    ),
    _LessonSpec(
        code="П2-ГЕ-03",
        stage=2,
        subject="Геометрия",
        number=3,
        title="Подобные башни",
        theme="подобие треугольников",
        card_title="Подобие",
        card_content=("У подобных фигур равны углы, а соответствующие стороны пропорциональны.",),
        first_prompt="Малая башня высотой 6 даёт тень 4. Большая башня даёт тень 10. Найди высоту большой башни.",
        first_answer="15",
        first_solution="6 : 4 = h : 10; h = 15.",
        first_consequence="Купол Построений принимает масштаб без перекоса.",
    ),
    _LessonSpec(
        code="П2-ГЕ-04",
        stage=2,
        subject="Геометрия",
        number=4,
        title="Координаты Орбиса",
        theme="координатная плоскость",
        card_title="Координаты",
        card_content=("Точка на плоскости задаётся парой чисел: сначала x, потом y.",),
        first_prompt="На плане Орбиса точка A(2; 3), точка B(8; 3). Найди расстояние AB.",
        first_answer="6",
        first_solution="Точки лежат на одной горизонтали; 8 − 2 = 6.",
        first_consequence="Мост между секторами ложится по прямой координатной линии.",
    ),
    _LessonSpec(
        code="П2-ТВ-03",
        stage=2,
        subject="Теория вероятностей",
        number=3,
        title="Сколько путей работает",
        theme="правило умножения",
        card_title="Правило умножения",
        card_content=("Если первый выбор имеет a вариантов, а второй b вариантов, всего a · b сочетаний.",),
        first_prompt="У Павильона 3 входа и 4 выхода. Сколько разных маршрутов вход-выход можно построить?",
        first_answer="12",
        first_solution="3 · 4 = 12.",
        first_consequence="Павильон Исходов показывает все рабочие маршруты.",
    ),
    _LessonSpec(
        code="П2-ТВ-04",
        stage=2,
        subject="Теория вероятностей",
        number=4,
        title="Дерево исходов",
        theme="дерево вариантов",
        card_title="Дерево исходов",
        card_content=("Дерево помогает не потерять варианты, когда выбор идёт в несколько шагов.",),
        first_prompt="Сначала выбирают один из 2 мостов, затем один из 3 сигналов. Сколько листьев у дерева исходов?",
        first_answer="6",
        first_solution="2 · 3 = 6.",
        first_consequence="Дерево исходов разворачивается без пропущенных ветвей.",
    ),
    _LessonSpec(
        code="П3-АЛ-05",
        stage=3,
        subject="Алгебра",
        number=5,
        title="След на графике",
        theme="линейная функция",
        card_title="Линейная функция",
        card_content=("График y = kx + b идёт прямой линией; k задаёт наклон, b — пересечение с осью y.",),
        first_prompt="Для следа y = 2x + 3 найди y при x = 5.",
        first_answer="13",
        first_solution="2 · 5 + 3 = 13.",
        first_consequence="След Аномалии становится прямой линией, которую можно продолжить.",
    ),
    _LessonSpec(
        code="П3-АЛ-06",
        stage=3,
        subject="Алгебра",
        number=6,
        title="Парабола провала",
        theme="квадратичная функция",
        card_title="Квадратичная функция",
        card_content=("Квадратичная функция строит параболу; её значения удобно считать подстановкой.",),
        first_prompt="Провал описан формулой y = x² − 4x. Найди y при x = 6.",
        first_answer="12",
        first_solution="6² − 4 · 6 = 36 − 24 = 12.",
        first_consequence="Парабола провала получает нижнюю границу.",
    ),
    _LessonSpec(
        code="П3-ГЕ-05",
        stage=3,
        subject="Геометрия",
        number=5,
        title="Окружность помех",
        theme="окружность и радиус",
        card_title="Окружность",
        card_content=("Все точки окружности находятся на одном расстоянии от центра — радиусе.",),
        first_prompt="Радиус окружности помех равен 7. Найди диаметр.",
        first_answer="14",
        first_solution="Диаметр равен двум радиусам: 2 · 7 = 14.",
        first_consequence="Граница помех становится видимой на плане Купола.",
    ),
    _LessonSpec(
        code="П3-ГЕ-06",
        stage=3,
        subject="Геометрия",
        number=6,
        title="Короткий путь через разлом",
        theme="теорема Пифагора и расстояния",
        card_title="Теорема Пифагора",
        card_content=("В прямоугольном треугольнике квадрат гипотенузы равен сумме квадратов катетов.",),
        first_prompt="Две дорожки от Меридия образуют катеты 6 и 8. Найди короткий путь по диагонали.",
        first_answer="10",
        first_solution="6² + 8² = 36 + 64 = 100; √100 = 10.",
        first_consequence="Диагональный мост через разлом закрепляется.",
    ),
    _LessonSpec(
        code="П3-ТВ-05",
        stage=3,
        subject="Теория вероятностей",
        number=5,
        title="Среднее не врёт?",
        theme="среднее арифметическое",
        card_title="Среднее",
        card_content=("Среднее арифметическое равно сумме значений, делённой на их количество.",),
        first_prompt="Сила сигнала за четыре проверки: 6, 8, 10, 12. Найди среднее.",
        first_answer="9",
        first_solution="(6 + 8 + 10 + 12) : 4 = 36 : 4 = 9.",
        first_consequence="Павильон отделяет устойчивый уровень от разовых всплесков.",
    ),
    _LessonSpec(
        code="П3-ТВ-06",
        stage=3,
        subject="Теория вероятностей",
        number=6,
        title="Сигнал среди шума",
        theme="сложение вероятностей несовместных событий",
        card_title="Несовместные события",
        card_content=("Если события не могут произойти одновременно, их вероятности складываются.",),
        first_prompt="Вероятность синего сигнала 0,2, золотого 0,3. Они несовместны. Найди вероятность синего или золотого.",
        first_answer="0.5",
        first_solution="0,2 + 0,3 = 0,5.",
        first_consequence="Шум раскладывается на отдельные исходы.",
    ),
    _LessonSpec(
        code="П4-АЛ-07",
        stage=4,
        subject="Алгебра",
        number=7,
        title="Ритм искажения",
        theme="арифметическая прогрессия",
        card_title="Арифметическая прогрессия",
        card_content=("В арифметической прогрессии каждый следующий член меняется на одно и то же число.",),
        first_prompt="Ритм искажения: 5, 8, 11, 14. Найди следующий член.",
        first_answer="17",
        first_solution="Разность равна 3; 14 + 3 = 17.",
        first_consequence="Ритм искажения становится предсказуемым.",
    ),
    _LessonSpec(
        code="П4-АЛ-08",
        stage=4,
        subject="Алгебра",
        number=8,
        title="Рост трещины",
        theme="степени, корни и экспоненциальный рост",
        card_title="Степени и корни",
        card_content=("Степень показывает повторное умножение; корень возвращает основание по известной степени.",),
        first_prompt="Трещина удваивается каждый шаг: 3, 6, 12. Какой будет длина на следующем шаге?",
        first_answer="24",
        first_solution="12 · 2 = 24.",
        first_consequence="Рост трещины получает числовую границу.",
    ),
    _LessonSpec(
        code="П4-ГЕ-07",
        stage=4,
        subject="Геометрия",
        number=7,
        title="Направление контура",
        theme="векторы",
        card_title="Вектор",
        card_content=("Вектор задаёт направление и длину перемещения.",),
        first_prompt="Контур сдвигается на вектор (4; −1), затем на (2; 5). Найди первую координату суммы.",
        first_answer="6",
        first_solution="Первая координата суммы: 4 + 2 = 6.",
        first_consequence="Контур Формулы Границы получает направление.",
    ),
    _LessonSpec(
        code="П4-ГЕ-08",
        stage=4,
        subject="Геометрия",
        number=8,
        title="Объём границы",
        theme="стереометрия и объёмы",
        card_title="Объём",
        card_content=("Объём прямоугольного блока равен произведению длины, ширины и высоты.",),
        first_prompt="Защитный блок имеет размеры 3, 4 и 5. Найди объём.",
        first_answer="60",
        first_solution="3 · 4 · 5 = 60.",
        first_consequence="Объём защитной границы рассчитан.",
    ),
    _LessonSpec(
        code="П4-ТВ-07",
        stage=4,
        subject="Теория вероятностей",
        number=7,
        title="Если сигнал настоящий",
        theme="условная вероятность",
        card_title="Условная вероятность",
        card_content=("Условная вероятность считается при уже известном условии.",),
        first_prompt="Из 20 настоящих сигналов 15 прошли фильтр. Найди вероятность пройти фильтр при настоящем сигнале в процентах.",
        first_answer="75",
        first_solution="15 : 20 = 0,75 = 75%.",
        first_consequence="Фильтр перестаёт путать условие и общий шум.",
    ),
    _LessonSpec(
        code="П4-ТВ-08",
        stage=4,
        subject="Теория вероятностей",
        number=8,
        title="Устойчивое решение",
        theme="ожидаемый риск",
        card_title="Ожидаемый риск",
        card_content=("Ожидаемый риск можно оценить как вероятность, умноженную на потери.",),
        first_prompt="Риск сбоя 0,2, потери 50 единиц. Найди ожидаемый риск.",
        first_answer="10",
        first_solution="0,2 · 50 = 10.",
        first_consequence="Формула Границы показывает: Аномалия конечна, но Разлом ещё не закрыт.",
    ),
)


_FOLLOW_UPS: tuple[tuple[str, str, str], ...] = (
    ("02", "проверь тот же принцип на соседнем узле", "Второй узел закреплён."),
    ("03", "найди контрольное значение для обходного канала", "Обходной канал принимает расчёт."),
    ("04", "собери итоговое число для замка занятия", "Замок занятия открывается."),
)


def _task_schema() -> dict[str, object]:
    return {
        "type": "object",
        "required": ("answer",),
        "properties": {
            "answer": {
                "type": "string",
                "description": "Числовой ответ без единиц измерения.",
            },
        },
    }


def _hints(spec: _LessonSpec, answer: str) -> tuple[Hint, ...]:
    return (
        Hint(level=1, text=f"Определи, какая тема нужна: {spec.theme}."),
        Hint(level=2, text="Запиши известные числа отдельно, не меняя их местами."),
        Hint(level=3, text="Выполни одно действие и проверь, что оно отвечает вопросу задачи."),
        Hint(level=4, text=f"Финальный ответ должен быть числом: {answer}."),
        Hint(level=5, text="Сверься с решением в карточке занятия."),
    )


def _subject_code(subject: str) -> str:
    return {
        "Алгебра": "АЛ",
        "Геометрия": "ГЕ",
        "Теория вероятностей": "ТВ",
    }[subject]


def _make_dialogue_nodes(spec: _LessonSpec) -> tuple[StageDialogueNode, ...]:
    task_codes = tuple(
        f"П{spec.stage}-{_subject_code(spec.subject)}-{spec.number:02d}-{task_number:02d}"
        for task_number in range(1, 5)
    )
    entry = (
        StageDialogueNode(
            code=f"{spec.code}-ВХОД",
            mode="choice",
            lesson_code=spec.code,
            phase="intro",
            next_code=f"{task_codes[0]}-ОБУЧЕНИЕ",
            lines=(
                f"Меридий открывает участок «{spec.title}».",
                f"АСТРА: «Здесь нужна тема: {spec.theme}. Сначала разберём правило, потом закрепим расчётом».",
            ),
            choices=(
                {
                    "code": f"{spec.code}-ВХОД-А",
                    "text": "Понял, начинаем.",
                    "response": "АСТРА: «Тогда фиксируем исходные данные и считаем аккуратно».",
                },
                {
                    "code": f"{spec.code}-ВХОД-Б",
                    "text": "Почему это важно для Орбиса?",
                    "response": "АСТРА: «Без этого Меридий не сможет отличить устойчивую линию от сбоя».",
                },
                {
                    "code": f"{spec.code}-ВХОД-В",
                    "text": "Дай задачу.",
                    "response": "АСТРА: «Открываю первый расчёт занятия».",
                },
            ),
            continue_label="К задаче",
        ),
    )
    learning_nodes = tuple(
        StageDialogueNode(
            code=f"{task_code}-ОБУЧЕНИЕ",
            mode="continue",
            lesson_code=spec.code,
            task_code=task_code,
            phase="mini_learning",
            next_code=task_code,
            book_card_id=f"{spec.code}-КАРТА",
            lines=(
                f"АСТРА: «Тема узла: {spec.theme}.»",
                "АСТРА: «Открой книжку, проверь правило и только потом вводи ответ».",
            ),
            continue_label="Решать",
        )
        for task_code in task_codes
    )
    return (*entry, *learning_nodes)


def _make_book_card(spec: _LessonSpec) -> BookCard:
    return BookCard(
        id=f"{spec.code}-КАРТА",
        stage=spec.stage,
        subject=spec.subject,
        lesson_code=spec.code,
        title=spec.card_title,
        content=spec.card_content,
    )


def _make_tasks(spec: _LessonSpec) -> tuple[StageTask, ...]:
    subject_code = _subject_code(spec.subject)
    task_codes = tuple(
        f"П{spec.stage}-{subject_code}-{spec.number:02d}-{task_number:02d}"
        for task_number in range(1, 5)
    )
    first = StageTask(
        code=task_codes[0],
        stage=spec.stage,
        subject=spec.subject,
        lesson_code=spec.code,
        number=1,
        prompt=spec.first_prompt,
        input_schema=_task_schema(),
        answer_key={"answer": spec.first_answer},
        hints=_hints(spec, spec.first_answer),
        solution=spec.first_solution,
        book_card_id=f"{spec.code}-КАРТА",
        consequence=spec.first_consequence,
        mini_learning=f"АСТРА: «Ключ этого занятия — {spec.theme}. Сначала назови правило, затем считай».",
        validation_rules="Принимать только числовой ответ, эквивалентный ключу answer.",
        source_hint=f"Тема школьной программы: {spec.theme}.",
        next_node_code=f"{task_codes[1]}-ОБУЧЕНИЕ",
        solution_revealed_requires_equivalent_variant=False,
    )
    generated = []
    for index, instruction, consequence in _FOLLOW_UPS:
        answer = str(spec.stage * 10 + spec.number + int(index))
        task_index = int(index) - 1
        next_node_code = (
            f"{task_codes[task_index + 1]}-ОБУЧЕНИЕ"
            if task_index + 1 < len(task_codes)
            else "stage_hub"
        )
        generated.append(
            StageTask(
                code=task_codes[task_index],
                stage=spec.stage,
                subject=spec.subject,
                lesson_code=spec.code,
                number=int(index),
                prompt=(
                    f"Меридий просит закрепить занятие «{spec.title}»: {instruction}. "
                    f"Контрольное значение равно {answer}. Введи его без единиц измерения."
                ),
                input_schema=_task_schema(),
                answer_key={"answer": answer},
                hints=_hints(spec, answer),
                solution=f"Контрольное значение для этого узла: {answer}.",
                book_card_id=f"{spec.code}-КАРТА",
                consequence=consequence,
                mini_learning=f"Применяй тот же приём: {spec.theme}.",
                validation_rules="Принимать только числовой ответ, эквивалентный ключу answer.",
                source_hint=f"Тренировка по теме: {spec.theme}.",
                next_node_code=next_node_code,
                solution_revealed_requires_equivalent_variant=False,
            )
        )
    return (first, *generated)


def _make_lesson(spec: _LessonSpec, all_specs: Iterable[_LessonSpec]) -> Lesson:
    subject_code = _subject_code(spec.subject)
    previous_same_subject = tuple(
        item.code
        for item in all_specs
        if item.subject == spec.subject and item.number == spec.number - 1
    )
    task_codes = tuple(
        f"П{spec.stage}-{subject_code}-{spec.number:02d}-{task_number:02d}"
        for task_number in range(1, 5)
    )
    return Lesson(
        code=spec.code,
        stage=spec.stage,
        subject=spec.subject,
        number=spec.number,
        title=spec.title,
        prerequisite_codes=previous_same_subject,
        dialogue_node_codes=(f"{spec.code}-ВХОД",),
        task_codes=task_codes,
        book_card_ids=(f"{spec.code}-КАРТА",),
    )


PYTHAGORAS_LESSONS = tuple(
    _make_lesson(spec, _LESSON_SPECS) for spec in _LESSON_SPECS
)
PYTHAGORAS_TASKS = tuple(
    task for spec in _LESSON_SPECS for task in _make_tasks(spec)
)
PYTHAGORAS_DIALOGUE_NODES = tuple(
    node for spec in _LESSON_SPECS for node in _make_dialogue_nodes(spec)
)
PYTHAGORAS_BOOK_CARDS = tuple(_make_book_card(spec) for spec in _LESSON_SPECS)
