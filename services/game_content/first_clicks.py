"""Allowed first-click explanation targets on the Earth/Indaris map (spec §4.6).

Зал Роста (Growth Hall) is deliberately absent: it has no click/route yet.
"""

from __future__ import annotations


FIRST_CLICK_TARGETS: frozenset[str] = frozenset({
    "earth.shop",
    "earth.stark_portal",
    "earth.trophy_hall",
    "indaris.dispatch",
    "indaris.server",
    "indaris.mining",
})
