"""Highlighter tests (owner: M07)."""
from pdpa_shield.engine.highlight import highlight_pattern

SAMPLE = r"""(?<![\d-])        # boundary
(?P<g1>\d{4})(?P<sep>[-\x20]?)(?P=sep)(?:a|b)+"""


def test_lossless():
    assert "".join(t for _, t in highlight_pattern(SAMPLE)) == SAMPLE


def test_classes():
    toks = highlight_pattern(SAMPLE)
    by = {}
    for cls, txt in toks:
        by.setdefault(cls, []).append(txt)
    assert "(?<!" in by["look"]
    assert "(?P<g1>" in by["named"]
    assert "(?P=sep)" in by["backref"]
    assert "(?:" in by["noncap"]
    assert r"[\d-]" in by["cls"] and r"[-\x20]" in by["cls"]
    assert "{4}" in by["quant"] and "+" in by["quant"]
    assert r"\d" in by["escape"]
    assert "|" in by["alt"]
    assert any(t.startswith("# boundary") for t in by["comment"])
