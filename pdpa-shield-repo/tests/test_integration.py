"""End-to-end: every canonical case through the real engine + real rules (owner: M01).

These pass only when M02–M07 are all done — this is the "definition of done" for the project.
"""
import pytest

from pdpa_shield.cases import CASES
from pdpa_shield.engine.registry import RULES
from pdpa_shield.engine.scanner import mask_text


@pytest.mark.parametrize("cat,neg,th,en,inp,expected", CASES, ids=[f"{c[0]}:{c[3]}" for c in CASES])
def test_case(cat, neg, th, en, inp, expected):
    if any(r.pattern is None for r in RULES):
        raise NotImplementedError("waiting for all five rules")
    assert mask_text(inp, RULES) == expected


def test_generated_logs_are_fully_detected():
    """Every PII item the generator inserts must be masked (catches regex gaps)."""
    from pdpa_shield.loggen import generate
    if any(r.pattern is None for r in RULES):
        raise NotImplementedError("waiting for all five rules")
    masked = mask_text(generate(300, seed=11), RULES)
    assert "@company.com" not in masked or "*" in masked
    for line in masked.splitlines():
        assert "card=" not in line or "XXXX" in line.split("card=")[1][:20]
