"""Acceptance tests for rules/address.py (owner: M06). Uses apply_single — no engine needed."""
import pytest

from pdpa_shield.cases import cases_for
from pdpa_shield.engine.types import apply_single
from pdpa_shield.rules import address

CASES = cases_for("address")


@pytest.mark.parametrize("cat,neg,th,en,inp,expected", CASES, ids=[c[3] for c in CASES])
def test_case(cat, neg, th, en, inp, expected):
    assert apply_single(address.RULE, inp) == expected


def test_pattern_is_verbose_and_documented():
    pattern = address.RULE.pattern
    if pattern is None:
        raise NotImplementedError("pattern not written yet")
    import re
    assert pattern.flags & re.VERBOSE, "write the pattern with re.VERBOSE and comment each line"
    assert address.RULE.explain_th and address.RULE.explain_en, "fill in explain_th / explain_en"


def test_named_groups():
    if address.RULE.pattern is None:
        raise NotImplementedError
    m = address.RULE.pattern.search(CASES[0][4])
    for g in ("prefix", "house", "soi", "road", "subdistrict", "district", "province"):
        assert m.group(g), g
    assert m.group("house") == "689"


def test_does_not_cross_lines():
    if address.RULE.pattern is None:
        raise NotImplementedError
    text = "Address: 12\nถนนสุขุมวิท แขวงคลองตัน เขตคลองเตย กรุงเทพฯ"
    assert address.RULE.pattern.search(text) is None
