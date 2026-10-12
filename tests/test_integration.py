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
    """Every labelled value the generator writes is either masked (valid) or reported (malformed)."""
    import re

    from pdpa_shield.engine.scanner import scan
    from pdpa_shield.engine.validate import find_issues
    from pdpa_shield.loggen import generate
    if any(r.pattern is None for r in RULES):
        raise NotImplementedError("waiting for all five rules")

    clean = mask_text(generate(300, seed=11, error_rate=0), RULES)
    for line in clean.splitlines():
        assert "card=" not in line or "XXXX" in line.split("card=")[1][:20]

    text = generate(300, seed=12)
    covered, pos = [], 0
    for part in scan(text, RULES):
        n = len(part["text"] if part["kind"] == "text" else part["original"])
        if part["kind"] == "pii":
            covered.append((pos, pos + n))
        pos += n
    covered += [(i["start"], i["end"]) for i in find_issues(text, {r.key: r.pattern for r in RULES})]
    for m in re.finditer(r"(?:card|tel|email)=", text):
        assert any(s <= m.end() + 1 < e or s == m.end() for s, e in covered), text[m.start():m.start() + 40]
