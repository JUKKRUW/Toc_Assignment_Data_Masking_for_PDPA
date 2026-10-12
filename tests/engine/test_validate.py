"""Validation tests: malformed personal data must be reported, valid data must not (owner: M07)."""
import pytest

from pdpa_shield.engine.registry import RULES
from pdpa_shield.engine.validate import find_issues

P = {r.key: r.pattern for r in RULES}

BAD = [
    ("card = 1234-ฟ123-2345-1536", "card", "ฟ"),
    ("x 12345-6789-0123-4567 y", "card", "17"),
    ("ref 1234-5678 9012-3456", "card", "ปน"),
    ("tel=093-245-789", "phone", "9 หลัก"),
    ("tel=193-245-7894", "phone", "0 หรือ +66"),
    ("email=user@localhost", "email", "นามสกุล"),
    ("email=a@@b.com", "email", "@"),
    ("DOB:32/13/2549", "dob", "32"),
    ("DOB:25/12/2006", "dob", "2006"),
    ("Address: ไม่ระบุ", "address", "เลขที่บ้าน"),
]
GOOD = [
    "card=1234-5678-9012-3456 | tel=093-245-7894 | email=somchai.d@company.com",
    "card=1234 5678 9012 3456 | tel=+66 91-666-8661 | DOB:25/12/2549",
    "Address: 689 ซอยลาดกระบัง 19 ถนนลาดกระบัง แขวงลาดกระบัง เขตลาดกระบัง กรุงเทพฯ",
    "2026-09-24 08:01:00 [INFO ] LOGIN session=685931 | ip=10.2.3.4 | txn_id=12345678901234567890",
    "ถนน ลาด กระบัง แขวง",
]


def _need_rules():
    if any(p is None for p in P.values()):
        raise NotImplementedError("waiting for all five rules")


@pytest.mark.parametrize("text,rule,needle", BAD, ids=[b[0] for b in BAD])
def test_reports_malformed(text, rule, needle):
    _need_rules()
    issues = find_issues(text, P)
    assert len(issues) == 1, issues
    assert issues[0]["rule"] == rule
    assert needle in issues[0]["reason_th"]
    assert issues[0]["reason_en"]
    assert text[issues[0]["start"]:issues[0]["end"]] == issues[0]["text"]


@pytest.mark.parametrize("text", GOOD)
def test_valid_data_has_no_issues(text):
    _need_rules()
    assert find_issues(text, P) == []


def test_line_numbers_and_enabled_filter():
    _need_rules()
    text = "ok\nDOB:32/13/2549\ncard=1234-ฟ123-2345-1536"
    assert [(i["rule"], i["line"]) for i in find_issues(text, P)] == [("dob", 2), ("card", 3)]
    assert [i["rule"] for i in find_issues(text, P, enabled=["card"])] == ["card"]
