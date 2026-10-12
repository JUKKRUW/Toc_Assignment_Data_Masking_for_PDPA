"""Risk score tests (owner: M07)."""
import re

from pdpa_shield.engine.risk import stats
from pdpa_shield.engine.types import Rule


def _rule(key, w):
    return Rule(key=key, label_th="", label_en="", color="#000", weight=w, pattern=re.compile("x"), replace=str)


RULES = [_rule("card", 5), _rule("email", 1), _rule("phone", 2), _rule("dob", 3), _rule("address", 3)]


def _pii(key):
    return {"kind": "pii", "rule": key, "original": "", "masked": "", "match": "", "groups": {}, "info": None}


def test_none():
    s = stats([{"kind": "text", "text": "hello"}], RULES)
    assert s["total"] == 0 and s["risk"] == 0 and s["level_code"] == "none" and s["level"] == "ไม่พบ"
    assert set(s["counts"]) == {"card", "email", "phone", "dob", "address"}


def test_one_of_each_is_mid():
    s = stats([_pii(k) for k in ("card", "email", "phone", "dob", "address")], RULES)
    assert s["risk"] == 28 and s["level_code"] == "mid" and s["level"] == "กลาง"


def test_cap_and_high():
    s = stats([_pii("card")] * 20, RULES)
    assert s["risk"] == 100 and s["level_code"] == "high"


def test_low():
    s = stats([_pii("email")], RULES)
    assert s["risk"] == 2 and s["level_code"] == "low"
