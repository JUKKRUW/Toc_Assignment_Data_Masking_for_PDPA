"""Acceptance tests for rules/phone.py (owner: M04). Uses apply_single — no engine needed."""
import pytest

from pdpa_shield.cases import cases_for
from pdpa_shield.engine.types import apply_single
from pdpa_shield.rules import phone

CASES = cases_for("phone")


@pytest.mark.parametrize("cat,neg,th,en,inp,expected", CASES, ids=[c[3] for c in CASES])
def test_case(cat, neg, th, en, inp, expected):
    assert apply_single(phone.RULE, inp) == expected


def test_pattern_is_verbose_and_documented():
    pattern = phone.RULE.pattern
    if pattern is None:
        raise NotImplementedError("pattern not written yet")
    import re
    assert pattern.flags & re.VERBOSE, "write the pattern with re.VERBOSE and comment each line"
    assert phone.RULE.explain_th and phone.RULE.explain_en, "fill in explain_th / explain_en"
