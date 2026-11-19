"""Declarative Game shop catalog."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ShopItemDefinition:
    id: str
    title: str
    description: str
    price_sircoins: int
    enabled: bool = True


SHOP_ITEMS: tuple[ShopItemDefinition, ...] = (
    ShopItemDefinition(
        id="learning_replay",
        title="Повтор мини-обучения",
        description="Повторить объяснение перед текущей задачей без штрафа.",
        price_sircoins=10,
    ),
    ShopItemDefinition(
        id="astra_hint",
        title="Мягкая подсказка Астры",
        description="Дополнительная подсказка к текущей задаче без потери звезды.",
        price_sircoins=20,
    ),
    ShopItemDefinition(
        id="attempt_stabilizer",
        title="Стабилизатор попытки",
        description="Один раз защищает текущую задачу от штрафа за следующую ошибку.",
        price_sircoins=40,
    ),
    ShopItemDefinition(
        id="grimoire_marker",
        title="Маркер Гримуара",
        description="Отложенный указатель на нужную карточку знания.",
        price_sircoins=25,
        enabled=False,
    ),
)


SHOP_ITEMS_BY_ID = {item.id: item for item in SHOP_ITEMS}


ASTRA_HINT_FALLBACK = (
    "АСТРА: «Посмотри на условие как на схему: сначала выпиши, что уже известно, "
    "потом выбери правило из карточки знания и только после этого подставляй числа»."
)

ATTEMPT_STABILIZER_HINT = (
    "АСТРА: «Стабилизатор поймал ошибку. Эта попытка не засчитана: звезда на месте, "
    "шкала помощи не выросла. Проверь расчёт ещё раз»."
)
