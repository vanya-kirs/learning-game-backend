"""Approved Game prologue dialogue and MVP map content."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, Mapping

from .models import DialogueNode


DDO_NODE_CODE = "ПР-04"
_DDO_PROFILES = frozenset(("chp", "cht", "chch", "chz", "chkh"))
_INDARIS_HANDOFF = (
    "\nАСТРА: «Переход подготовлен. На месте покажу три здания и общий список проверок»."
)


def _question(code: str, text: str, response: str) -> dict[str, str]:
    return {"code": code, "text": text, "response": response}


def _choice(code: str, text: str, response: str) -> dict[str, str]:
    return {"code": code, "text": text, "response": response}


@dataclass(frozen=True)
class InterfaceAction:
    id: str
    from_state: str
    to_state: str
    instruction: str


@dataclass(frozen=True)
class OnboardingActionNode:
    code: str
    lines: tuple[str, ...]
    initial_state: str
    completed_state: str
    actions: tuple[InterfaceAction, ...]
    mode: Literal["action"] = "action"
    questions: tuple[Mapping[str, str], ...] = ()
    choices: tuple[Mapping[str, str], ...] = ()
    continue_label: str = ""

    @property
    def action_ids(self) -> tuple[str, ...]:
        return tuple(action.id for action in self.actions)

    def apply_action(self, state: str, action_id: str) -> str:
        for action in self.actions:
            if action.id == action_id:
                if state != action.from_state:
                    raise ValueError(
                        f"Action {action_id} requires state {action.from_state}"
                    )
                return action.to_state
        raise ValueError(f"Unknown action for {self.code}: {action_id}")

    def is_complete(self, state: str) -> bool:
        return state == self.completed_state


ONBOARDING_NODES = (
    DialogueNode(
        code="ПР-01",
        mode="choice",
        lines=(
            "АСТРА: «Есть контакт. Разрыв задел узел связи. Мне нужна помощь здесь, на площадке».",
            "АСТРА: «Я Астра. Объясню, что случилось, как только удержим связь. Открой отмеченную панель».",
        ),
        choices=(
            _choice("ПР-01-А", "Я помогу. Покажи, что делать.", "АСТРА: «Выделяю панель. Буду рядом на каждом шаге»."),
            _choice("ПР-01-Б", "Я не умею чинить такие вещи.", "АСТРА: «Сейчас достаточно освоить управление. Начнём с одного действия»."),
            _choice("ПР-01-В", "Мне нужно понять, где я.", "АСТРА: «На главной базе, на Земле. Ты в безопасной зоне управления. Помоги удержать канал, затем расскажу подробнее»."),
        ),
    ),
    OnboardingActionNode(
        code="ПР-Д01",
        lines=(
            "АСТРА: «Открой выделенную панель, выбери подписанный резервный канал и подтверди подключение. Это три действия в интерфейсе».",
        ),
        initial_state="panel_closed",
        completed_state="connection_confirmed",
        actions=(
            InterfaceAction(
                id="open_highlighted_panel",
                from_state="panel_closed",
                to_state="panel_open",
                instruction=(
                    "Открой выделенную панель. "
                    "Нужная панель отмечена кольцом."
                ),
            ),
            InterfaceAction(
                id="select_backup_channel",
                from_state="panel_open",
                to_state="backup_channel_selected",
                instruction="Выбери подписанный резервный канал.",
            ),
            InterfaceAction(
                id="confirm_connection",
                from_state="backup_channel_selected",
                to_state="connection_confirmed",
                instruction="Подтверди подключение.",
            ),
        ),
    ),
    DialogueNode(
        code="ПР-02",
        mode="questions",
        lines=(
            "АСТРА: «Получилось. Связь удержали. Прости за такую встречу. Теперь можно спокойно».",
            "АСТРА: «Разрыв начался несколько недель назад. Сбои идут по разным планетам: меняются данные, болеют живые системы, техника теряет управление».",
            "АСТРА: «Из чёрной дыры вырвалась Аномалия. Она вмешивается в работу миров. Нам нужно разобраться с последствиями и подготовиться к поиску источника».",
            "АСТРА: «Система отбора выбрала тебя среди множества кандидатов. Почему именно тебя — полного ответа у меня пока нет».",
        ),
        questions=(
            _question("ПР-02-В-01", "Разрыв и Аномалия — одно и то же?", "АСТРА: «Разрывом мы называем происходящее с мирами. Аномалия — сила, которая вмешивается в них. Это связанные, но разные вещи»."),
            _question("ПР-02-В-02", "Почему наставники не справятся сами?", "АСТРА: «Их инструменты и знания тоже сталкиваются со сбоями. Нужны проверки, свежий взгляд и помощь между направлениями»."),
            _question("ПР-02-В-03", "Мне придётся всё решать без помощи?", "АСТРА: «Нет. Я объясняю основы, наставники помогают понять задачи. Но расчёты и решения останутся твоими»."),
        ),
        continue_label="Хочу понять, как учиться",
    ),
    DialogueNode(
        code="ПР-03",
        mode="choice",
        lines=(
            "АСТРА: «Перед каждой учебной задачей будет короткое объяснение. После него формула, пример и условия появятся в цифровой книжке знаний. Её можно открыть во время решения».",
        ),
        choices=(
            _choice("ПР-03-А", "Я попробую сначала сам.", "АСТРА: «Хорошо. Если понадобится, книжка и подсказки останутся доступны»."),
            _choice("ПР-03-Б", "Лучше буду сверяться с примером.", "АСТРА: «Для этого он и сохранён. В самой задаче будут другие данные»."),
            _choice("ПР-03-В", "А если ошибусь несколько раз?", "АСТРА: «Разберём конкретный шаг и попробуем снова. Ошибка в расчёте не означает поражение в истории»."),
        ),
    ),
    OnboardingActionNode(
        code="ПР-Д02",
        lines=(
            "Обязательное действие: открыть цифровую книжку знаний и вернуться.",
        ),
        initial_state="book_closed",
        completed_state="book_returned",
        actions=(
            InterfaceAction(
                id="open_knowledge_book",
                from_state="book_closed",
                to_state="book_open",
                instruction="Открой цифровую книжку знаний.",
            ),
            InterfaceAction(
                id="return_from_knowledge_book",
                from_state="book_open",
                to_state="book_returned",
                instruction="Вернись из книжки к онбордингу.",
            ),
        ),
    ),
    DialogueNode(
        code=DDO_NODE_CODE,
        mode="questions",
        lines=("АСТРА: «Сейчас отдельный опросник о твоих интересах. Это не проверка знаний: здесь не нужно угадывать правильный ответ».",),
        questions=(
            _question("ПР-04-В-01", "Результат запретит мне другие направления?", "АСТРА: «Нет. Он помогает выбрать начало, а не закрывает остальные возможности»."),
            _question("ПР-04-В-02", "Мне отвечать про то, что уже умею?", "АСТРА: «Следуй инструкции самого опросника и отвечай о своих предпочтениях. Не выбирай то, что кажется престижнее»."),
            _question("ПР-04-В-03", "Можно сначала прочитать инструкцию?", "АСТРА: «Конечно. Она откроется перед вопросами в любом случае»."),
        ),
        continue_label="Открыть опросник",
    ),
    DialogueNode(
        code="ПР-05",
        mode="questions",
        lines=(
            "АСТРА: «Результат сохранён. Показываю фактический профиль по пяти направлениям».",
            "АСТРА: «У Шелдона — природа и естественные науки. У Старка — техника, информатика и ИИ. У Черчилля — люди, языки и общество. У Пифагора — математика. У Маяковского — язык и искусство».",
            "АСТРА: «Для общей истории понадобится помощь всех направлений. В текущей версии доступна экспедиция к Старку; результат диагностики при этом сохраняется таким, каким получился».",
        ),
        questions=(
            _question("ПР-05-В-01", "А если мне ближе другое направление?", "АСТРА: «Это отражено в твоём профиле. Доступность экспедиции сейчас связана с готовностью этой версии, а не с заменой результата»."),
            _question("ПР-05-В-02", "Чем отличаются проблемы планет?", "АСТРА: «У Шелдона меняются живые системы, у Старка сбоит техника, у Черчилля — связь, доверие и понимание, у Пифагора — вычисления, у Маяковского — тексты и искусство»."),
            _question("ПР-05-В-03", "Можно вернуться на главную базу?", "АСТРА: «Да. На Индарисе для этого служит Компас — центральное здание-телепорт»."),
        ),
        continue_label="Связаться со Старком",
    ),
    DialogueNode(
        code="ПР-06",
        mode="questions",
        lines=(
            "СТАРК: «Связь есть. На Индарисе адреса меняются сами, дроны теряют протоколы, роботы повторяют команды. Часть работы остановлена».",
            "СТАРК: «Нам нужны три вещи: проверенные данные, понятные команды и техника, которую можно испытать. Начнёшь с того, что выберешь, но одной службой не обойдёмся».",
        ),
        questions=(
            _question("ПР-06-В-01", "Что случилось с дронами?", "СТАРК: «Один застыл над площадкой и перестал отвечать обычным командам. Мы прекратили его работу. На карте сейчас летающих дронов нет»."),
            _question("ПР-06-В-02", "Ты думаешь, кто-то меняет команды?", "СТАРК: «Есть подозрение. Доказательства будем искать в записях и проверках, а не в догадках»."),
            _question("ПР-06-В-03", "С чего бы ты начал?", "СТАРК: «С диспетчерской — мне важно понять адреса. Но серверная и рудник тоже готовы к первичной проверке. Выбор за тобой»."),
        ),
        continue_label="Я понял задачу",
    ),
    DialogueNode(
        code="ПР-07",
        mode="choice",
        lines=(),
        choices=(
            _choice("ПР-07-А", "Начну с данных.", "СТАРК: «Посмотри диспетчерскую. После перехода сможешь подтвердить выбор или передумать»." + _INDARIS_HANDOFF),
            _choice("ПР-07-Б", "Мне интереснее Компас.", "СТАРК: «Тогда серверная. Сначала разберём его данные, обучение будет позже»." + _INDARIS_HANDOFF),
            _choice("ПР-07-В", "Хочу разобраться с роботом.", "СТАРК: «Рудник. Машина на стенде, комплектующие доступны. Самостоятельный запуск пока закрыт»." + _INDARIS_HANDOFF),
            _choice("ПР-07-Г", "Сначала осмотрюсь.", "СТАРК: «Правильно. Я останусь на связи. Все три первых занятия доступны»." + _INDARIS_HANDOFF),
        ),
    ),
)


def _location(
    *,
    profile: str,
    mentor: str,
    title: str,
    description: str,
    image_asset: str | None = None,
    mentor_asset: str | None = None,
    local_astra_point: str | None = None,
    map_points: tuple[Mapping[str, str], ...] = (),
) -> Mapping[str, object]:
    values: dict[str, object] = {
        "profile": profile,
        "mentor": mentor,
        "title": title,
        "description": description,
        "status": "soon",
    }
    if image_asset:
        values["image_asset"] = image_asset
    if mentor_asset:
        values["mentor_asset"] = mentor_asset
    if local_astra_point:
        values["local_astra_point"] = local_astra_point
    if map_points:
        values["map_points"] = map_points
    return MappingProxyType(
        values
    )


MAP_LOCATIONS: Mapping[str, Mapping[str, object]] = MappingProxyType(
    {
        "stark_indaris": _location(
            profile="cht",
            mentor="Старк",
            title="Индарис",
            description="Техника, информатика и ИИ",
        ),
        "sheldon": _location(
            profile="chp",
            mentor="Шелдон",
            title="Эйдосфера",
            description="Физика, химия, биология и география",
        ),
        "churchill": _location(
            profile="chch",
            mentor="Черчилль",
            title="Конкордия",
            description="Английский язык, обществознание и всеобщая история",
            image_asset="subjects/Черчилль ЧЧ/Карта/concordia-approved.png",
            mentor_asset="subjects/Черчилль ЧЧ/Образ/churchill-approved.png",
            local_astra_point="Логос",
            map_points=(
                {
                    "id": "logos",
                    "title": "Логос",
                    "subject": "Астра",
                    "position": "center",
                    "description": "Центральный смысловой узел Конкордии",
                },
                {
                    "id": "english_academy",
                    "title": "Английская академия",
                    "subject": "Иностранный язык (английский)",
                    "position": "top_left",
                    "description": "Дом иностранного языка: перевод, контекст и дипломатические формулировки",
                },
                {
                    "id": "accord_chamber",
                    "title": "Палата Согласия",
                    "subject": "Обществознание",
                    "position": "top_right",
                    "description": "Дом правил, ответственности, прав и границ согласия",
                },
                {
                    "id": "historical_paths_house",
                    "title": "Дом Исторических Путей",
                    "subject": "Всеобщая история",
                    "position": "bottom",
                    "description": "Дом исторической памяти, союзов, кризисов и договоров",
                },
            ),
        ),
        "pythagoras": _location(
            profile="chz",
            mentor="Пифагор",
            title="Математика",
            description="Алгебра, геометрия и теория вероятностей",
        ),
        "mayakovsky": _location(
            profile="chkh",
            mentor="Маяковский",
            title="Язык и искусство",
            description="Русский язык, литература и МХК",
        ),
    }
)


def map_locations_after_klimov(profile: str) -> dict[str, dict[str, object]]:
    """Return the MVP map without replacing the student's factual DDO profile."""
    if profile not in _DDO_PROFILES:
        raise ValueError(f"Unknown Klimov profile: {profile}")

    locations = {code: dict(location) for code, location in MAP_LOCATIONS.items()}
    if profile == "chp":
        locations["sheldon"]["status"] = "available"
    elif profile == "chch":
        locations["churchill"]["status"] = "available"
    elif profile == "chz":
        locations["pythagoras"]["status"] = "available"
    elif profile == "chkh":
        locations["mayakovsky"]["status"] = "available"
    else:
        locations["stark_indaris"]["status"] = "available"
    return locations
