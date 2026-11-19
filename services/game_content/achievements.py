"""Declarative catalog of Game Trophy Hall achievements (spec §6)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AchievementDefinition:
    id: str
    category: str
    title: str
    description: str
    reward_sircoins: int
    enabled: bool = True


ACHIEVEMENTS: tuple[AchievementDefinition, ...] = (
    AchievementDefinition("intro_astra", "start", "Знакомство", "Первый разговор с Астрой", 10),
    AchievementDefinition("first_lesson", "start", "Первый шаг", "Закрыть первое занятие любого предмета", 20),
    AchievementDefinition("first_trophy_claim", "start", "Первый трофей", "Забрать первую награду в Трофейном зале", 15),
    AchievementDefinition("three_stars_any", "mastery", "Три звезды", "Получить 3★ на любом занятии", 30),
    AchievementDefinition("no_hints_lesson", "mastery", "Без подсказок", "Закрыть занятие с 0 подсказок", 35),
    AchievementDefinition("perfect_subject_stage", "mastery", "Идеальное крыло", "Получить 3★ на двух занятиях одного предмета внутри этапа", 60),
    AchievementDefinition("perfect_stage", "mastery", "Идеальный этап", "Получить 3★ на всех шести занятиях этапа", 120),
    AchievementDefinition("independent_streak_5", "mastery", "Самостоятельный", "Закрыть 5 занятий подряд без единой подсказки", 100),
    AchievementDefinition("dispatch_restored", "progress", "Диспетчер восстановлен", "Закрыть все доступные занятия Информатики в текущем этапе", 50),
    AchievementDefinition("server_restored", "progress", "Серверная ожила", "Закрыть все доступные занятия ИИ в текущем этапе", 50),
    AchievementDefinition("mining_restored", "progress", "Комплекс запущен", "Закрыть все доступные занятия Робототехники в текущем этапе", 50),
    AchievementDefinition("stage_complete", "progress", "Этап закрыт", "Закрыть все шесть занятий этапа", 90),
    AchievementDefinition("stark_branch_complete", "progress", "Ветка Старка пройдена", "Закрыть все четыре этапа ветки Старка", 250),
    AchievementDefinition("stage_echo_hunter", "exploration", "Эхо-охотник", "Найти все эхо-записи текущего этапа", 70, enabled=False),
    AchievementDefinition("first_voice", "exploration", "Голос Первого", "Собрать эхо-записи из двух и более разных предметов", 80, enabled=False),
    AchievementDefinition("rift_archivist", "exploration", "Архивариус Разрыва", "Открыть 24 записи общего ядра лора в ветке Старка", 110, enabled=False),
    AchievementDefinition("completed_with_stark_help", "behavior", "Не сдаюсь", "Довести занятие до конца даже с помощью Старка", 25),
    AchievementDefinition("last_chance_solved", "behavior", "Последняя попытка", "После 4-й подсказки решить задачу самому до вмешательства Старка", 40),
    AchievementDefinition("first_shop_purchase", "behavior", "Постоянный клиент", "Первая покупка в Магазине", 20),
    AchievementDefinition("improved_replay", "behavior", "Вернулся сильнее", "Перепройти занятие и улучшить лучший результат", 45),
    AchievementDefinition("window_shopper", "joke", "Я просто смотрю", "Открыть Магазин 5 раз, ничего не купив", 10, enabled=False),
    AchievementDefinition("stark_warning_seen", "joke", "Старк, не начинай", "Получить предупреждение Старка на 4-й подсказке впервые", 10),
)


def _build_index() -> dict[str, AchievementDefinition]:
    index: dict[str, AchievementDefinition] = {}
    for item in ACHIEVEMENTS:
        if item.id in index:
            raise ValueError(f"Duplicate achievement id: {item.id}")
        index[item.id] = item
    return index


ACHIEVEMENTS_BY_ID: dict[str, AchievementDefinition] = _build_index()


STARK_WARNING_LINES: tuple[str, ...] = (
    "СТАРК: «Ладно, даю последнюю попытку. Соберись: ещё один заход — и я уже заберу управление на себя».",
    "СТАРК: «Вижу, не справляешься. Я подержу систему ещё минуту, но это последняя самостоятельная попытка».",
    "СТАРК: «Последний шанс, герой. Потом я сделаю сам, а ты спокойно разберёшь, где именно всё поехало».",
)
