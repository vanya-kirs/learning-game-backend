"""DDO (Klimov) and EPI (Eysenck) scoring. DDO is taken in the game
onboarding; EPI is taken in the personal cabinet
(POST /web/school/students/{id}/epi in web_tests_router.py)."""
from __future__ import annotations

# ─────────────────────────────────────────────────────────────────
# DDO scoring key — аналитика_спека_полная_1.md (8 per type)
# key: frozenset of (question_number, answer) where answer='a'|'b'
# ─────────────────────────────────────────────────────────────────

_DDO_KEY: dict[str, frozenset[tuple[int, str]]] = {
    "chp":  frozenset({(1,'a'),(3,'b'),(6,'a'),(10,'a'),(11,'a'),(13,'b'),(16,'b'),(20,'a')}),
    "cht":  frozenset({(1,'b'),(4,'a'),(7,'b'),(9,'a'),(11,'b'),(14,'a'),(17,'b'),(19,'a')}),
    "chch": frozenset({(2,'a'),(4,'b'),(6,'b'),(8,'a'),(12,'a'),(14,'b'),(16,'a'),(18,'a')}),
    "chz":  frozenset({(2,'b'),(5,'a'),(9,'b'),(10,'b'),(12,'b'),(15,'a'),(19,'b'),(20,'b')}),
    "chkh": frozenset({(3,'a'),(5,'b'),(7,'a'),(8,'b'),(13,'a'),(15,'b'),(17,'a'),(18,'b')}),
}

_DDO_TYPE_LABELS = {"chp": "Ч-П", "cht": "Ч-Т", "chch": "Ч-Ч", "chz": "Ч-З", "chkh": "Ч-Х"}

# ─────────────────────────────────────────────────────────────────
# EPI scoring key — EPI_промт_полный.md (вариант А)
# ─────────────────────────────────────────────────────────────────

_EPI_EXTRAVERSION_YES = frozenset({1,3,8,10,13,17,22,25,27,39,44,46,49,53,56})
_EPI_EXTRAVERSION_NO  = frozenset({5,15,20,29,32,34,37,41,51})
_EPI_NEUROTISM_YES    = frozenset({2,4,7,9,11,14,16,19,21,23,26,28,31,33,35,38,40,43,45,47,50,52,55,57})
_EPI_LIE_YES          = frozenset({6,24,36})
_EPI_LIE_NO           = frozenset({12,18,30,42,48,54})


def score_ddo(answers: dict[str, str]) -> tuple[int, int, int, int, int, str]:
    """Compute DDO scores. answers: {"1": "a", "2": "b", ...}
    Returns (chp, cht, chch, chz, chkh, dominant).
    """
    parsed = {(int(q), a.lower()) for q, a in answers.items()}
    scores = {k: len(parsed & v) for k, v in _DDO_KEY.items()}
    max_score = max(scores.values())
    winners = [_DDO_TYPE_LABELS[k] for k, v in scores.items() if v == max_score]
    dominant = "/".join(winners)
    return scores["chp"], scores["cht"], scores["chch"], scores["chz"], scores["chkh"], dominant


def score_epi(answers: dict[str, bool]) -> tuple[int, int, int, str, str, str, bool]:
    """Compute EPI scores. answers: {"1": True, "2": False, ...}
    Returns (extraversion, neurotism, lie_scale, temperament, extraversion_level, neurotism_level, lie_valid).
    """
    yes_qs = {int(q) for q, v in answers.items() if v}
    no_qs  = {int(q) for q, v in answers.items() if not v}

    extraversion = len(yes_qs & _EPI_EXTRAVERSION_YES) + len(no_qs & _EPI_EXTRAVERSION_NO)
    neurotism    = len(yes_qs & _EPI_NEUROTISM_YES)
    lie_scale    = len(yes_qs & _EPI_LIE_YES) + len(no_qs & _EPI_LIE_NO)

    if extraversion >= 12 and neurotism < 12:
        temperament = "sanguine"
    elif extraversion >= 12 and neurotism >= 12:
        temperament = "choleric"
    elif extraversion < 12 and neurotism < 12:
        temperament = "phlegmatic"
    else:
        temperament = "melancholic"

    if extraversion > 19:
        extraversion_level = "bright_extravert"
    elif extraversion >= 15:
        extraversion_level = "extravert"
    elif extraversion >= 9:
        extraversion_level = "middle"
    elif extraversion >= 5:
        extraversion_level = "introvert"
    else:
        extraversion_level = "deep_introvert"

    if neurotism > 19:
        neurotism_level = "very_high"
    elif neurotism >= 14:
        neurotism_level = "high"
    elif neurotism >= 9:
        neurotism_level = "middle"
    else:
        neurotism_level = "low"

    lie_valid = lie_scale <= 4

    return extraversion, neurotism, lie_scale, temperament, extraversion_level, neurotism_level, lie_valid
