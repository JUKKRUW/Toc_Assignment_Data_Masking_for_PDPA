"""Log generator tests (owner: M08)."""
from pdpa_shield.loggen import generate


def test_line_count_and_newlines():
    text = generate(30, seed=1)
    assert text.endswith("\n") and len(text.splitlines()) == 30


def test_deterministic():
    assert generate(20, seed=7) == generate(20, seed=7)
    assert generate(20, seed=7) != generate(20, seed=8)


def test_contains_pii_and_decoys():
    text = generate(200, seed=3)
    for needle in ("@", "card=", "DOB:", "Address: ", "txn_id=", "ip="):
        assert needle in text, needle
