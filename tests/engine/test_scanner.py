"""Scanner tests (owner: M07). Uses FAKE rules so they do not depend on M02–M06."""
import re

from pdpa_shield.engine.scanner import mask_text, scan
from pdpa_shield.engine.types import Rule

LONG = Rule(key="card", label_th="", label_en="", color="#000", weight=5,
            pattern=re.compile(r"\d{4}-\d{4}"), replace=lambda m: "LONG")
SHORT = Rule(key="phone", label_th="", label_en="", color="#000", weight=2,
             pattern=re.compile(r"\d{4}"), replace=lambda m: "S")
TARGETED = Rule(key="address", label_th="", label_en="", color="#000", weight=3,
                pattern=re.compile(r"No\.(?P<house>\d+) (?P<road>\w+)"), replace=lambda m: "X", target="house")
EMPTY = Rule(key="email", label_th="", label_en="", color="#000", weight=1,
             pattern=None, replace=lambda m: "?")


def test_priority_and_overlap():
    # LONG runs first; SHORT must not re-match digits already inside LONG
    assert mask_text("a 1234-5678 b 9999", [LONG, SHORT]) == "a LONG b S"


def test_priority_order_matters():
    assert mask_text("1234-5678", [SHORT, LONG]) == "S-S"


def test_parts_are_lossless():
    text = "x 1234-5678 y 4321 z"
    parts = scan(text, [LONG, SHORT])
    original = "".join(p["text"] if p["kind"] == "text" else p["original"] for p in parts)
    assert original == text
    assert [p["rule"] for p in parts if p["kind"] == "pii"] == ["card", "phone"]


def test_target_group_only():
    parts = scan("go No.689 Sukhumvit now", [TARGETED])
    pii = [p for p in parts if p["kind"] == "pii"][0]
    assert pii["original"] == "689" and pii["masked"] == "X"
    assert pii["match"] == "No.689 Sukhumvit"
    assert pii["groups"] == {"house": "689", "road": "Sukhumvit"}
    assert mask_text("go No.689 Sukhumvit now", [TARGETED]) == "go No.X Sukhumvit now"


def test_enabled_filter_and_missing_pattern():
    assert mask_text("1234-5678", [LONG, SHORT, EMPTY], enabled=["phone"]) == "S-S"
    assert mask_text("abc", [EMPTY]) == "abc"


def test_empty_text():
    assert scan("", [LONG]) == []
