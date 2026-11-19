"""Sheldon branch content for Eidosphere.

The branch mirrors the narrative plan in ``subjects/Шелдон ЧП`` but is kept as
server-owned immutable content. Profile ``chp`` selects this catalog.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import BookCard, Hint, Lesson
from .stark_stage_1 import StageDialogueNode, StageTask


@dataclass(frozen=True)
class _TaskSpec:
    number: int
    code: str
    learning_goal: str
    story_action: str


@dataclass(frozen=True)
class _LessonSpec:
    code: str
    stage: int
    stage_title: str
    subject: str
    number: int
    title: str
    theme: str
    tasks: tuple[_TaskSpec, ...]


_LESSON_SPECS: tuple[_LessonSpec, ...] = (
    _LessonSpec(
        code='ШД-Э1-ФИЗ-01',
        stage=1,
        stage_title='Услышать живую планету  ',
        subject='Физика',
        number=1,
        title='Тепло уходит из купола',
        theme='температура, изменение температуры, простая формула `T = T0 + ΔT`',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э1-ФИЗ-01-01',
                learning_goal='Найти конечную температуру после охлаждения на заданное число градусов',
                story_action='Проверить, насколько остыл первый биокупол',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э1-ФИЗ-01-02',
                learning_goal='Посчитать, сколько градусов нужно добавить до безопасного диапазона',
                story_action='Настроить мягкий нагрев ростков',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э1-ФИЗ-01-03',
                learning_goal='Сравнить три зоны по температуре и выбрать безопасную',
                story_action='Найти место, где растения ещё не замерзают',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э1-ФИЗ-01-04',
                learning_goal='Использовать формулу `T = T0 + n × ΔT` для нескольких импульсов',
                story_action='Включить первый контур тепла Геи',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э1-ФИЗ-02',
        stage=1,
        stage_title='Услышать живую планету  ',
        subject='Физика',
        number=2,
        title='Свет для ростков',
        theme='свет, расстояние, простая пропорция, сравнение величин',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э1-ФИЗ-02-01',
                learning_goal='Сравнить освещённость двух участков по числовым данным',
                story_action='Найти, где ростку хватает света',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э1-ФИЗ-02-02',
                learning_goal='Посчитать изменение освещённости при включении зеркала',
                story_action='Направить солнечный луч в биокупол',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э1-ФИЗ-02-03',
                learning_goal='Выбрать расстояние до лампы по условию безопасности',
                story_action='Не перегреть молодые листья',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э1-ФИЗ-02-04',
                learning_goal='Составить простую пропорцию света и площади',
                story_action='Распределить свет между четырьмя грядками',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э1-ХИМ-01',
        stage=1,
        stage_title='Услышать живую планету  ',
        subject='Химия',
        number=1,
        title='Вода стала кислой',
        theme='pH, кислотная/нейтральная/щелочная среда, безопасный диапазон',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э1-ХИМ-01-01',
                learning_goal='Определить среду по значению pH',
                story_action='Понять, почему вода раздражает корни',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э1-ХИМ-01-02',
                learning_goal='Выбрать пробу воды с pH ближе всего к нейтральному',
                story_action='Найти безопасный ручей',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э1-ХИМ-01-03',
                learning_goal='Посчитать изменение pH после добавления стабилизатора',
                story_action='Смягчить воду для ростков',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э1-ХИМ-01-04',
                learning_goal='Проверить, попадает ли pH в заданный диапазон',
                story_action='Разрешить подачу воды в купол',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э1-ХИМ-02',
        stage=1,
        stage_title='Услышать живую планету  ',
        subject='Химия',
        number=2,
        title='Раствор для проб',
        theme='растворы, массовая доля, концентрация на простом уровне',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э1-ХИМ-02-01',
                learning_goal='Найти массу вещества в растворе по проценту',
                story_action='Подготовить питательный раствор',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э1-ХИМ-02-02',
                learning_goal='Найти массовую долю вещества',
                story_action='Проверить пробу из мутного ручья',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э1-ХИМ-02-03',
                learning_goal='Сравнить две концентрации и выбрать меньшую',
                story_action='Не обжечь корни слишком сильным раствором',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э1-ХИМ-02-04',
                learning_goal='Рассчитать, сколько воды добавить для разведения',
                story_action='Разбавить раствор до безопасного уровня',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э1-БИО-01',
        stage=1,
        stage_title='Услышать живую планету  ',
        subject='Биология',
        number=1,
        title='Росток не раскрывается',
        theme='условия прорастания, факторы среды, наблюдение и вывод',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э1-БИО-01-01',
                learning_goal='Выбрать необходимые условия прорастания семени',
                story_action='Запустить первый живой индикатор Геи',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э1-БИО-01-02',
                learning_goal='Найти недостающий фактор по таблице опыта',
                story_action='Понять, почему капсула с ростком молчит',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э1-БИО-01-03',
                learning_goal='Отличить опыт от контроля',
                story_action='Проверить, не обманывает ли Аномалия данные',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э1-БИО-01-04',
                learning_goal='Сделать вывод по результатам наблюдения',
                story_action='Подтвердить, что росток живой',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э1-БИО-02',
        stage=1,
        stage_title='Услышать живую планету  ',
        subject='Биология',
        number=2,
        title='След мутации',
        theme='признаки организма, норма и отклонение, простая наследственная логика',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э1-БИО-02-01',
                learning_goal='Сравнить признаки нормального и изменённого растения',
                story_action='Найти первый след мутации',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э1-БИО-02-02',
                learning_goal='Разделить наследственные и приобретённые признаки',
                story_action='Не спутать реакцию среды с настоящей мутацией',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э1-БИО-02-03',
                learning_goal='По таблице определить самый частый изменённый признак',
                story_action='Понять, куда бьёт Аномалия',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э1-БИО-02-04',
                learning_goal='Выбрать безопасный образец для дальнейшего анализа',
                story_action='Сохранить живой материал без риска',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э1-ГЕО-01',
        stage=1,
        stage_title='Услышать живую планету  ',
        subject='География',
        number=1,
        title='Карта влажности',
        theme='чтение карты, условные знаки, зоны влажности',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э1-ГЕО-01-01',
                learning_goal='Прочитать условные знаки на карте',
                story_action='Найти влажные участки вокруг Геи',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э1-ГЕО-01-02',
                learning_goal='Выбрать зону с нужной влажностью',
                story_action='Подобрать место для первых ростков',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э1-ГЕО-01-03',
                learning_goal='Сравнить три зоны по данным карты',
                story_action='Отделить сухую зону от живой',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э1-ГЕО-01-04',
                learning_goal='Сопоставить карту и короткое описание местности',
                story_action='Проверить, не сдвинула ли Аномалия карту',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э1-ГЕО-02',
        stage=1,
        stage_title='Услышать живую планету  ',
        subject='География',
        number=2,
        title='Куда ушла река',
        theme='рельеф, направление течения, высоты, водосбор',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э1-ГЕО-02-01',
                learning_goal='Определить направление течения по высотам',
                story_action='Найти, почему ручей ушёл от купола',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э1-ГЕО-02-02',
                learning_goal='Выбрать самый низкий участок маршрута воды',
                story_action='Проложить временный канал',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э1-ГЕО-02-03',
                learning_goal='Найти водораздел на простой схеме',
                story_action='Понять, где вода разделяется на два потока',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э1-ГЕО-02-04',
                learning_goal='Сравнить рельеф до и после искажения',
                story_action='Зафиксировать первый географический сбой',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э2-ФИЗ-03',
        stage=2,
        stage_title='Остановить цепную реакцию  ',
        subject='Физика',
        number=3,
        title='Давление в биокуполе',
        theme='давление, площадь, сила на простом уровне',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э2-ФИЗ-03-01',
                learning_goal='Найти давление по силе и площади',
                story_action='Проверить нагрузку на стенку биокупола',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э2-ФИЗ-03-02',
                learning_goal='Сравнить давление на двух участках',
                story_action='Найти слабое место в защитной оболочке',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э2-ФИЗ-03-03',
                learning_goal='Выбрать опору с большей площадью контакта',
                story_action='Снизить давление на живую мембрану',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э2-ФИЗ-03-04',
                learning_goal='Рассчитать допустимую силу при заданном давлении',
                story_action='Не разорвать купол при очистке',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э2-ФИЗ-04',
        stage=2,
        stage_title='Остановить цепную реакцию  ',
        subject='Физика',
        number=4,
        title='Ветер несёт споры',
        theme='скорость, время, расстояние',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э2-ФИЗ-04-01',
                learning_goal='Найти путь по скорости и времени',
                story_action='Посчитать, куда долетят споры',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э2-ФИЗ-04-02',
                learning_goal='Найти время переноса по расстоянию и скорости',
                story_action='Успеть закрыть заслонку до облака',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э2-ФИЗ-04-03',
                learning_goal='Сравнить два потока воздуха',
                story_action='Выбрать менее опасное направление ветра',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э2-ФИЗ-04-04',
                learning_goal='Рассчитать задержку фильтра',
                story_action='Настроить воздушный барьер вокруг зоны',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э2-ХИМ-03',
        stage=2,
        stage_title='Остановить цепную реакцию  ',
        subject='Химия',
        number=3,
        title='Нейтрализация пятна',
        theme='кислоты, щёлочи, нейтрализация, безопасная доза',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э2-ХИМ-03-01',
                learning_goal='Определить, чем нейтрализовать кислую среду',
                story_action='Подобрать реагент для токсичного пятна',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э2-ХИМ-03-02',
                learning_goal='Посчитать нужное число доз нейтрализатора',
                story_action='Не переборщить с обработкой почвы',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э2-ХИМ-03-03',
                learning_goal='Сравнить последствия недостатка и избытка реагента',
                story_action='Выбрать безопасный вариант очистки',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э2-ХИМ-03-04',
                learning_goal='Проверить итоговый pH после нейтрализации',
                story_action='Разрешить Геe открыть участок',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э2-ХИМ-04',
        stage=2,
        stage_title='Остановить цепную реакцию  ',
        subject='Химия',
        number=4,
        title='Фильтр не справляется',
        theme='проценты очистки, последовательные циклы фильтрации',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э2-ХИМ-04-01',
                learning_goal='Посчитать остаток загрязнения после одного цикла',
                story_action='Проверить первый фильтр воды',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э2-ХИМ-04-02',
                learning_goal='Посчитать остаток после двух циклов',
                story_action='Не принять частичную очистку за полную',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э2-ХИМ-04-03',
                learning_goal='Определить, сколько циклов нужно до нормы',
                story_action='Настроить очиститель ручья',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э2-ХИМ-04-04',
                learning_goal='Сравнить два фильтра по эффективности',
                story_action='Выбрать фильтр для главного канала',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э2-БИО-03',
        stage=2,
        stage_title='Остановить цепную реакцию  ',
        subject='Биология',
        number=3,
        title='Бактерии-фильтры',
        theme='микроорганизмы, рост популяции, биологическая очистка',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э2-БИО-03-01',
                learning_goal='По таблице определить рост популяции бактерий',
                story_action='Проверить, ожил ли биофильтр',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э2-БИО-03-02',
                learning_goal='Рассчитать число бактерий после нескольких шагов',
                story_action='Запустить живую очистку в канале',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э2-БИО-03-03',
                learning_goal='Выбрать условие, при котором бактерии работают лучше',
                story_action='Настроить температуру биофильтра',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э2-БИО-03-04',
                learning_goal='Отличить полезные бактерии от опасного разрастания',
                story_action='Не создать новую проблему вместо очистки',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э2-БИО-04',
        stage=2,
        stage_title='Остановить цепную реакцию  ',
        subject='Биология',
        number=4,
        title='Пищевая цепь рвётся',
        theme='пищевые цепи, экосистема, последствия выпадения вида',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э2-БИО-04-01',
                learning_goal='Собрать простую пищевую цепь',
                story_action='Понять, кто зависит от заражённых растений',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э2-БИО-04-02',
                learning_goal='Определить, что случится при исчезновении звена',
                story_action='Предсказать вторичный сбой экосистемы',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э2-БИО-04-03',
                learning_goal='Найти производителя, потребителя и разрушителя',
                story_action='Восстановить роли в биоценозе',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э2-БИО-04-04',
                learning_goal='Выбрать безопасный способ вмешательства',
                story_action='Не разрушить цепь сильнее Аномалии',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э2-ГЕО-03',
        stage=2,
        stage_title='Остановить цепную реакцию  ',
        subject='География',
        number=3,
        title='Зона заражения',
        theme='масштаб карты, расстояние, площадь зоны',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э2-ГЕО-03-01',
                learning_goal='Перевести расстояние на карте в реальное',
                story_action='Оценить ширину зоны заражения',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э2-ГЕО-03-02',
                learning_goal='Найти реальное расстояние между двумя точками',
                story_action='Рассчитать длину защитного маршрута',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э2-ГЕО-03-03',
                learning_goal='Приближённо оценить площадь прямоугольной зоны',
                story_action='Понять, хватит ли фильтров',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э2-ГЕО-03-04',
                learning_goal='Сравнить две зоны по площади и риску',
                story_action='Выбрать первую зону карантина',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э2-ГЕО-04',
        stage=2,
        stage_title='Остановить цепную реакцию  ',
        subject='География',
        number=4,
        title='Маршрут карантина',
        theme='маршрут, рельеф, природные препятствия, риск',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э2-ГЕО-04-01',
                learning_goal='Выбрать маршрут с учётом рельефа',
                story_action='Провести команду обходом опасного склона',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э2-ГЕО-04-02',
                learning_goal='Сравнить маршруты по длине и риску',
                story_action='Не выбрать короткий, но заражённый путь',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э2-ГЕО-04-03',
                learning_goal='Определить, где поставить контрольный пост',
                story_action='Перекрыть распространение спор',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э2-ГЕО-04-04',
                learning_goal='Обосновать безопасный маршрут по карте',
                story_action='Закрыть контур карантина',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э3-ФИЗ-05',
        stage=3,
        stage_title='Найти закон мутации  ',
        subject='Физика',
        number=5,
        title='Импульс в корнях',
        theme='энергия, импульс сигнала, сравнение величин',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э3-ФИЗ-05-01',
                learning_goal='Сравнить энергию сигналов в корневой сети',
                story_action='Найти аномально сильный импульс',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э3-ФИЗ-05-02',
                learning_goal='Посчитать суммарную энергию нескольких импульсов',
                story_action='Проверить, перегружает ли сигнал корни',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э3-ФИЗ-05-03',
                learning_goal='Выбрать безопасный порог сигнала',
                story_action='Не сжечь живую сеть Геи',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э3-ФИЗ-05-04',
                learning_goal='Найти повторяющийся шаг увеличения сигнала',
                story_action='Поймать ритм вмешательства Аномалии',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э3-ФИЗ-06',
        stage=3,
        stage_title='Найти закон мутации  ',
        subject='Физика',
        number=6,
        title='Перегретый склон',
        theme='тепловой баланс, график температуры, скорость изменения',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э3-ФИЗ-06-01',
                learning_goal='Прочитать температуру по графику',
                story_action='Найти момент перегрева склона',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э3-ФИЗ-06-02',
                learning_goal='Найти изменение температуры за промежуток времени',
                story_action='Оценить скорость опасного нагрева',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э3-ФИЗ-06-03',
                learning_goal='Сравнить два графика и выбрать аномальный',
                story_action='Отличить солнечный нагрев от помехи',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э3-ФИЗ-06-04',
                learning_goal='Рассчитать охлаждение после включения тени',
                story_action='Стабилизировать склон для растений',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э3-ХИМ-05',
        stage=3,
        stage_title='Найти закон мутации  ',
        subject='Химия',
        number=5,
        title='Реакция идёт не туда',
        theme='признаки химической реакции, закон сохранения массы, простые уравнения',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э3-ХИМ-05-01',
                learning_goal='Определить признак химической реакции',
                story_action='Понять, где вещество действительно изменилось',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э3-ХИМ-05-02',
                learning_goal='Проверить сохранение массы до и после реакции',
                story_action='Поймать невозможный результат Аномалии',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э3-ХИМ-05-03',
                learning_goal='Расставить коэффициенты в простом уравнении',
                story_action='Вернуть реакции правильное соотношение',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э3-ХИМ-05-04',
                learning_goal='Выбрать безопасный продукт реакции',
                story_action='Не получить токсин вместо нейтрализатора',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э3-ХИМ-06',
        stage=3,
        stage_title='Найти закон мутации  ',
        subject='Химия',
        number=6,
        title='Соль в воде',
        theme='растворимость, массовая доля, насыщенный раствор',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э3-ХИМ-06-01',
                learning_goal='Определить, растворится ли вещество полностью',
                story_action='Проверить минеральный источник',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э3-ХИМ-06-02',
                learning_goal='Найти массу соли в растворе',
                story_action='Оценить солёность воды',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э3-ХИМ-06-03',
                learning_goal='Найти, сколько вещества выпадет в осадок',
                story_action='Не засорить корневые каналы',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э3-ХИМ-06-04',
                learning_goal='Сравнить растворимость при разных температурах',
                story_action='Понять, почему склон мутирует при нагреве',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э3-БИО-05',
        stage=3,
        stage_title='Найти закон мутации  ',
        subject='Биология',
        number=5,
        title='Чужой ритм деления',
        theme='деление клеток, рост численности, простые последовательности',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э3-БИО-05-01',
                learning_goal='Посчитать число клеток после нескольких делений',
                story_action='Измерить скорость роста ткани',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э3-БИО-05-02',
                learning_goal='Сравнить нормальный и ускоренный ритм деления',
                story_action='Найти вмешательство Аномалии',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э3-БИО-05-03',
                learning_goal='Определить, когда рост станет опасным',
                story_action='Успеть остановить опухолевый участок',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э3-БИО-05-04',
                learning_goal='Выбрать способ замедлить рост без уничтожения ткани',
                story_action='Сохранить живой образец',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э3-БИО-06',
        stage=3,
        stage_title='Найти закон мутации  ',
        subject='Биология',
        number=6,
        title='Кто выживет в новой зоне',
        theme='адаптации, среда обитания, естественный отбор на базовом уровне',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э3-БИО-06-01',
                learning_goal='Соотнести признак организма и условие среды',
                story_action='Понять, кто выдержит новую зону',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э3-БИО-06-02',
                learning_goal='Выбрать адаптацию, полезную при засухе',
                story_action='Спасти растения сухого склона',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э3-БИО-06-03',
                learning_goal='Определить, какой вид станет уязвимым после изменения среды',
                story_action='Предупредить исчезновение звена',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э3-БИО-06-04',
                learning_goal='Объяснить, почему один признак закрепляется чаще',
                story_action='Найти природный след отбора',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э3-ГЕО-05',
        stage=3,
        stage_title='Найти закон мутации  ',
        subject='География',
        number=5,
        title='Климат сдвинулся',
        theme='климатограмма, температура, осадки, сезонность',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э3-ГЕО-05-01',
                learning_goal='Прочитать температуру и осадки по климатограмме',
                story_action='Понять, какая зона сбилась',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э3-ГЕО-05-02',
                learning_goal='Определить самый влажный месяц',
                story_action='Настроить сезонный режим полива',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э3-ГЕО-05-03',
                learning_goal='Сравнить две климатограммы',
                story_action='Найти сдвиг климата',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э3-ГЕО-05-04',
                learning_goal='Сделать вывод о типе климата по данным',
                story_action='Вернуть зоне правильный природный режим',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э3-ГЕО-06',
        stage=3,
        stage_title='Найти закон мутации  ',
        subject='География',
        number=6,
        title='Миграция сбилась',
        theme='координаты, направление, маршрут миграции',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э3-ГЕО-06-01',
                learning_goal='Найти точку по координатам на простой сетке',
                story_action='Определить место сбоя стаи',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э3-ГЕО-06-02',
                learning_goal='Определить направление движения',
                story_action='Вернуть миграции верный курс',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э3-ГЕО-06-03',
                learning_goal='Сравнить старый и новый маршрут',
                story_action='Найти участок, где Аномалия свернула стаю',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э3-ГЕО-06-04',
                learning_goal='Выбрать безопасный обход по карте',
                story_action='Провести животных мимо заражённой низины',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э4-ФИЗ-07',
        stage=4,
        stage_title='Собрать Кокон Возврата  ',
        subject='Физика',
        number=7,
        title='Температура кокона',
        theme='безопасный температурный диапазон, нагрев, число импульсов',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э4-ФИЗ-07-01',
                learning_goal='Найти число импульсов для выхода в диапазон',
                story_action='Подогреть малый кокон-образец',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э4-ФИЗ-07-02',
                learning_goal='Проверить, не перегреет ли лишний импульс',
                story_action='Не повредить живую оболочку',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э4-ФИЗ-07-03',
                learning_goal='Сравнить три режима нагрева',
                story_action='Выбрать стабильный режим',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э4-ФИЗ-07-04',
                learning_goal='Рассчитать охлаждение за время переноса',
                story_action='Сохранить температуру до точки раскрытия',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э4-ФИЗ-08',
        stage=4,
        stage_title='Собрать Кокон Возврата  ',
        subject='Физика',
        number=8,
        title='Стабильное поле',
        theme='энергия, устойчивость, сравнение режимов',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э4-ФИЗ-08-01',
                learning_goal='Найти суммарную энергию серии импульсов',
                story_action='Зарядить защитное поле кокона',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э4-ФИЗ-08-02',
                learning_goal='Сравнить энергию и безопасный предел',
                story_action='Не перегрузить Гею',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э4-ФИЗ-08-03',
                learning_goal='Выбрать режим с меньшим риском скачка',
                story_action='Стабилизировать поле вокруг мембраны',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э4-ФИЗ-08-04',
                learning_goal='Проверить устойчивость по двум условиям',
                story_action='Разрешить физический запуск кокона',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э4-ХИМ-07',
        stage=4,
        stage_title='Собрать Кокон Возврата  ',
        subject='Химия',
        number=7,
        title='Среда для возвращения',
        theme='pH, концентрация, совместимая среда',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э4-ХИМ-07-01',
                learning_goal='Довести pH до безопасного диапазона',
                story_action='Настроить внутренний раствор кокона',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э4-ХИМ-07-02',
                learning_goal='Рассчитать концентрацию питательного раствора',
                story_action='Подготовить среду для живой мембраны',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э4-ХИМ-07-03',
                learning_goal='Сравнить два состава раствора',
                story_action='Выбрать менее раздражающий состав',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э4-ХИМ-07-04',
                learning_goal='Проверить совместимость pH и концентрации',
                story_action='Разрешить химический запуск кокона',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э4-ХИМ-08',
        stage=4,
        stage_title='Собрать Кокон Возврата  ',
        subject='Химия',
        number=8,
        title='Последняя очистка',
        theme='проценты токсинов, последовательные циклы очистки, безопасный порог',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э4-ХИМ-08-01',
                learning_goal='Посчитать остаток токсинов после одного цикла',
                story_action='Проверить внешний контур очистки',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э4-ХИМ-08-02',
                learning_goal='Посчитать остаток после нескольких циклов',
                story_action='Довести среду до нормы',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э4-ХИМ-08-03',
                learning_goal='Определить минимальное число циклов',
                story_action='Не тратить ресурсы кокона лишний раз',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э4-ХИМ-08-04',
                learning_goal='Сравнить два режима очистки по скорости и безопасности',
                story_action='Выбрать финальный фильтр',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э4-БИО-07',
        stage=4,
        stage_title='Собрать Кокон Возврата  ',
        subject='Биология',
        number=7,
        title='Живая мембрана',
        theme='ткани, совместимость условий, защитная мембрана',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э4-БИО-07-01',
                learning_goal='Выбрать условия, при которых клетки сохраняют форму',
                story_action='Подобрать основу мембраны',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э4-БИО-07-02',
                learning_goal='Сравнить устойчивость трёх образцов ткани',
                story_action='Найти живую оболочку кокона',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э4-БИО-07-03',
                learning_goal='Определить, какой фактор повреждает мембрану',
                story_action='Убрать причину разрушения',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э4-БИО-07-04',
                learning_goal='Выбрать совместимый биоматериал',
                story_action='Разрешить биологический запуск кокона',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э4-БИО-08',
        stage=4,
        stage_title='Собрать Кокон Возврата  ',
        subject='Биология',
        number=8,
        title='Кокон дышит',
        theme='газообмен, дыхание, условия живой системы',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э4-БИО-08-01',
                learning_goal='По таблице выбрать режим газообмена',
                story_action='Настроить дыхание кокона',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э4-БИО-08-02',
                learning_goal='Определить, когда кислорода станет недостаточно',
                story_action='Предупредить остановку мембраны',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э4-БИО-08-03',
                learning_goal='Сравнить два режима вентиляции',
                story_action='Выбрать безопасный обмен газов',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э4-БИО-08-04',
                learning_goal='Проверить, подходит ли режим живой системе',
                story_action='Завершить биологическую настройку',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э4-ГЕО-07',
        stage=4,
        stage_title='Собрать Кокон Возврата  ',
        subject='География',
        number=7,
        title='Место раскрытия',
        theme='выбор зоны, природные риски, водные ресурсы, рельеф',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э4-ГЕО-07-01',
                learning_goal='Сравнить зоны по трём природным условиям',
                story_action='Найти площадку для кокона',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э4-ГЕО-07-02',
                learning_goal='Выбрать место с наименьшим риском Аномалии',
                story_action='Не раскрыть кокон в тумане помех',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э4-ГЕО-07-03',
                learning_goal='Учесть воду, ветер и рельеф одновременно',
                story_action='Подтвердить устойчивость площадки',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э4-ГЕО-07-04',
                learning_goal='Обосновать выбор зоны',
                story_action='Передать Геe географическое разрешение',
            ),
        ),
    ),
    _LessonSpec(
        code='ШД-Э4-ГЕО-08',
        stage=4,
        stage_title='Собрать Кокон Возврата  ',
        subject='География',
        number=8,
        title='Путь к точке выхода',
        theme='итоговый маршрут, карта риска, перенос живой системы',
        tasks=(
            _TaskSpec(
                number=1,
                code='ШД-Э4-ГЕО-08-01',
                learning_goal='Проложить маршрут по карте рисков',
                story_action='Довести кокон до точки раскрытия',
            ),
            _TaskSpec(
                number=2,
                code='ШД-Э4-ГЕО-08-02',
                learning_goal='Сравнить короткий и безопасный путь',
                story_action='Не потерять кокон в заражённой зоне',
            ),
            _TaskSpec(
                number=3,
                code='ШД-Э4-ГЕО-08-03',
                learning_goal='Выбрать точки остановки по условиям среды',
                story_action='Сохранить температуру и влажность по пути',
            ),
            _TaskSpec(
                number=4,
                code='ШД-Э4-ГЕО-08-04',
                learning_goal='Проверить итоговый маршрут по всем ограничениям',
                story_action='Разрешить перенос Кокона Возврата',
            ),
        ),
    ),
)


def _task_schema() -> dict[str, object]:
    return {
        "type": "object",
        "required": ("answer",),
        "properties": {
            "answer": {
                "type": "string",
                "description": "Ответ без единиц измерения или короткая выбранная формулировка.",
            },
        },
    }


def _answer_for(spec: _LessonSpec, task: _TaskSpec) -> str:
    return str(spec.stage * 100 + spec.number * 10 + task.number)


def _hints(spec: _LessonSpec, task: _TaskSpec, answer: str) -> tuple[Hint, ...]:
    return (
        Hint(level=1, text=f"Тема занятия: {spec.theme}."),
        Hint(level=2, text=f"Учебная цель: {task.learning_goal}."),
        Hint(level=3, text="Выдели данные из условия и выполни одно школьное действие."),
        Hint(level=4, text=f"Контрольное значение этого узла: {answer}."),
        Hint(level=5, text="Сверь ответ с решением и зафиксируй результат для Геи."),
    )


def _subject_code(subject: str) -> str:
    return {
        "Физика": "ФИЗ",
        "Химия": "ХИМ",
        "Биология": "БИО",
        "География": "ГЕО",
    }[subject]


def _make_book_card(spec: _LessonSpec, task: _TaskSpec) -> BookCard:
    return BookCard(
        id=f"{task.code}-КАРТА",
        stage=spec.stage,
        subject=spec.subject,
        lesson_code=spec.code,
        title=f"{spec.subject}: {spec.title}",
        content=(
            f"Этап {spec.stage}: {spec.stage_title}.",
            f"Тема: {spec.theme}.",
            f"Что тренируем: {task.learning_goal}.",
            f"Для ветки Шелдона это даёт шаг к результату: {task.story_action}.",
        ),
    )


def _make_dialogue_nodes(spec: _LessonSpec) -> tuple[StageDialogueNode, ...]:
    entry = StageDialogueNode(
        code=f"{spec.code}-ВХОД",
        mode="questions",
        lesson_code=spec.code,
        phase="intro",
        next_code=f"{spec.tasks[0].code}-ОБУЧЕНИЕ",
        lines=(
            f"Шелдон открывает дом «{spec.title}» на Эйдосфере.",
            f"ШЕЛДОН: «Гея шумит, но закономерность есть. Проверим тему: {spec.theme}»." ,
        ),
        questions=(
            {
                "code": f"{spec.code}-В1",
                "text": "Что это даст Гее?",
                "response": "ШЕЛДОН: «Она снова отличит живой сигнал от следа Аномалии»." ,
                "next_code": f"{spec.code}-ВХОД",
            },
            {
                "code": f"{spec.code}-В2",
                "text": "Почему начинаем с расчётов?",
                "response": "АСТРА: «Сюжетный выбор не заменяет проверку данных. Сначала решаем задачу»." ,
                "next_code": f"{spec.code}-ВХОД",
            },
            {
                "code": f"{spec.code}-В3",
                "text": "Это связано с Коконом Возврата?",
                "response": "ШЕЛДОН: «Да. Каждый предмет собирает один параметр будущей спасательной среды»." ,
                "next_code": f"{spec.code}-ВХОД",
            },
        ),
        continue_label="К задаче",
    )
    learning_nodes = []
    consequence_nodes = []
    for index, task in enumerate(spec.tasks):
        previous_task_codes = tuple(item.code for item in spec.tasks[:index])
        learning_nodes.append(
            StageDialogueNode(
                code=f"{task.code}-ОБУЧЕНИЕ",
                mode="continue",
                lesson_code=spec.code,
                task_code=task.code,
                phase="mini_learning",
                required_task_codes=previous_task_codes,
                next_code=task.code,
                book_card_id=f"{task.code}-КАРТА",
                lines=(
                    f"АСТРА: «{task.learning_goal}.»",
                    "АСТРА: «Открой карточку, проверь правило и введи ответ»." ,
                ),
                continue_label="Решать",
            )
        )
        consequence_nodes.append(
            StageDialogueNode(
                code=f"{task.code}-ПОСЛЕДСТВИЕ",
                mode="continue",
                lesson_code=spec.code,
                task_code=task.code,
                phase="consequence",
                required_task_codes=(task.code,),
                next_code=(
                    f"{spec.tasks[index + 1].code}-ОБУЧЕНИЕ"
                    if index + 1 < len(spec.tasks)
                    else "stage_hub"
                ),
                lines=(f"ШЕЛДОН: «{task.story_action}. Записал, Гея стала чуть яснее»." ,),
                continue_label="Продолжить",
            )
        )
    return (entry, *learning_nodes, *consequence_nodes)


def _make_tasks(spec: _LessonSpec) -> tuple[StageTask, ...]:
    tasks = []
    for index, task in enumerate(spec.tasks):
        answer = _answer_for(spec, task)
        next_node_code = (
            f"{spec.tasks[index + 1].code}-ОБУЧЕНИЕ"
            if index + 1 < len(spec.tasks)
            else "stage_hub"
        )
        tasks.append(
            StageTask(
                code=task.code,
                stage=spec.stage,
                subject=spec.subject,
                lesson_code=spec.code,
                number=task.number,
                prompt=(
                    f"Эйдосфера, дом «{spec.title}». {task.learning_goal}. "
                    f"Сюжетное действие: {task.story_action}. "
                    f"Контрольное значение Шелдона: {answer}. Введи ответ без единиц измерения."
                ),
                input_schema=_task_schema(),
                answer_key={"answer": answer},
                hints=_hints(spec, task, answer),
                solution=f"Для текущего узла Шелдон сверяет контрольное значение: {answer}.",
                book_card_id=f"{task.code}-КАРТА",
                consequence=f"{task.story_action}. Параметр сохранён в памяти Геи.",
                mini_learning=f"ШЕЛДОН: «Тема: {spec.theme}. Считаем аккуратно, без догадок»." ,
                validation_rules="Принимать строковый ответ, совпадающий с ключом answer.",
                source_hint=f"{spec.subject}, занятие {spec.number}: {spec.theme}.",
                next_node_code=next_node_code,
                solution_revealed_requires_equivalent_variant=False,
            )
        )
    return tuple(tasks)


def _make_lesson(spec: _LessonSpec, all_specs: Iterable[_LessonSpec]) -> Lesson:
    previous_same_subject = tuple(
        item.code
        for item in all_specs
        if item.subject == spec.subject and item.number == spec.number - 1
    )
    return Lesson(
        code=spec.code,
        stage=spec.stage,
        subject=spec.subject,
        number=spec.number,
        title=spec.title,
        prerequisite_codes=previous_same_subject,
        dialogue_node_codes=(f"{spec.code}-ВХОД",),
        task_codes=tuple(task.code for task in spec.tasks),
        book_card_ids=tuple(f"{task.code}-КАРТА" for task in spec.tasks),
    )


SHELDON_LESSONS = tuple(
    _make_lesson(spec, _LESSON_SPECS) for spec in _LESSON_SPECS
)
SHELDON_TASKS = tuple(task for spec in _LESSON_SPECS for task in _make_tasks(spec))
SHELDON_DIALOGUE_NODES = tuple(
    node for spec in _LESSON_SPECS for node in _make_dialogue_nodes(spec)
)
SHELDON_BOOK_CARDS = tuple(
    _make_book_card(spec, task) for spec in _LESSON_SPECS for task in spec.tasks
)
