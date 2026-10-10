"""Acceptance tests for rules/card.py (owner: M02). Uses apply_single — no engine needed."""
import pytest

from pdpa_shield.cases import cases_for
from pdpa_shield.engine.types import apply_single
from pdpa_shield.rules import card

CASES = cases_for("card")


@pytest.mark.parametrize("cat,neg,th,en,inp,expected", CASES, ids=[c[3] for c in CASES])
def test_case(cat, neg, th, en, inp, expected):
    assert apply_single(card.RULE, inp) == expected


def test_pattern_is_verbose_and_documented():
    pattern = card.RULE.pattern
    if pattern is None:
        raise NotImplementedError("pattern not written yet")
    import re
    assert pattern.flags & re.VERBOSE, "write the pattern with re.VERBOSE and comment each line"
    assert card.RULE.explain_th and card.RULE.explain_en, "fill in explain_th / explain_en"


def test_named_group_last4():
    m = card.RULE.pattern.search("x 1234-5678-9012-3456 y") if card.RULE.pattern else None
    if m is None and card.RULE.pattern is None:
        raise NotImplementedError
    assert m.group("last4") == "3456"
