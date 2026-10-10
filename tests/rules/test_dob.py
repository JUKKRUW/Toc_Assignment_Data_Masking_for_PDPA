"""Acceptance tests for rules/dob.py (owner: M05). Uses apply_single — no engine needed."""
import pytest

from pdpa_shield.cases import cases_for
from pdpa_shield.engine.types import apply_single
from pdpa_shield.rules import dob

CASES = cases_for("dob")


@pytest.mark.parametrize("cat,neg,th,en,inp,expected", CASES, ids=[c[3] for c in CASES])
def test_case(cat, neg, th, en, inp, expected):
    assert apply_single(dob.RULE, inp) == expected


def test_pattern_is_verbose_and_documented():
    pattern = dob.RULE.pattern
    if pattern is None:
        raise NotImplementedError("pattern not written yet")
    import re
    assert pattern.flags & re.VERBOSE, "write the pattern with re.VERBOSE and comment each line"
    assert dob.RULE.explain_th and dob.RULE.explain_en, "fill in explain_th / explain_en"
