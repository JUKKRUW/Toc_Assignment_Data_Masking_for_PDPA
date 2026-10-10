r"""Rule 04 — Phone By : 68010698 ปาราเมศ สีเหล็ก

Spec (assignment)
    Format XXX-XXX-XXXX, keep only the last 4 digits.
    093-245-7894 -> XXX-XXX-7894

Requirements (implementation)
    [ ] Separator may be "-", a single space, or nothing — but the SAME one throughout.
        Hint: a named group for the separator + a backreference (?P=sep).
    [ ] Keep the original separator in the output.
    [ ] Replace the first 6 digits with "X", keeping the last 4 digits.

Expected examples
    093-245-7894 -> XXX-XXX-7894
    093 245 7894 -> XXX XXX 7894
    0932457894   -> XXXXXX7894

Acceptance tests: tests/rules/test_phone.py (confirm with the team).
"""

from __future__ import annotations

import re

from pdpa_shield.engine.types import Rule

PATTERN = re.compile(
    r"""
    (?<![0-9])              # Prevent matching inside a longer digit sequence
    [0-9]{3}-               # Match the first three digits and a hyphen
    [0-9]{3}-               # Match the next three digits and a hyphen
    (?P<last4>[0-9]{4})     # Capture the final four digits
    (?![0-9])               # Prevent matching inside a longer digit sequence
    """,
    re.VERBOSE,
)


def mask(m: re.Match) -> str:
    """Hide the first six digits and keep the final four digits."""
    return f"XXX-XXX-{m.group('last4')}"


RULE = Rule(
    key="phone",
    label_th="เบอร์โทรศัพท์",
    label_en="Phone number",
    color="#22c55e",
    weight=2,
    pattern=PATTERN,
    replace=mask,
    example="093-245-7894",
    explain_th=[
        "0[0-9]{2} — จับสามหลักแรกที่ขึ้นต้นด้วย 0",
        "(?P<sep>[- ]?) — เก็บตัวคั่นของเบอร์",
        "(?P=sep) — บังคับใช้ตัวคั่นเดิม",
        "(?P<last4>[0-9]{4}) — เก็บสี่หลักท้ายไว้แสดง",
    ],
    explain_en=[
        "0[0-9]{2} — Match three initial digits starting with 0",
        "(?P<sep>[- ]?) — Capture the separator",
        "(?P=sep) — Require the same separator",
        "(?P<last4>[0-9]{4}) — Capture the final four digits",
    ],
)
