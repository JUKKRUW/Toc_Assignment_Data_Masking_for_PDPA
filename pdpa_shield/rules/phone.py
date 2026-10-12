r"""Rule 03 — Phone number.                                        Owner: 68010698 ปาราเมศ สีเหล็ก

Spec (assignment)
    Format XXX-XXX-XXXX, keep only the last 4 digits.
    093-245-7894  ->  XXX-XXX-7894

Requirements
    [ ] Thai format 0xx-xxx-xxxx; also "0xx xxx xxxx" and "0xxxxxxxxx" (consistent separator).
    [ ] International format "+66 93-245-7894" -> "+66 XX-XXX-7894" (hint: alternation).
    [ ] Must NOT match "123-456-7890" (no leading 0) or "093-245-78945" (too many digits).
    [ ] Named group `last4`.
    [ ] Mask with re.sub(r"\d", "X", ...) on everything except the last 4 digits.
    [ ] re.VERBOSE with a comment on every line; fill in explain_th / explain_en.

Note: the engine runs the card rule BEFORE this one, so you do not need to worry about
digits that are part of a credit card number.

Acceptance tests: tests/rules/test_phone.py
"""
from __future__ import annotations

import re

from pdpa_shield.engine.types import Rule

PATTERN: re.Pattern | None = re.compile(
    r"""
    (?<![\d+-])
    (?:
        (?P<intl>\+66)[-\x20]?(?P<p1i>[1-9]\d)   # +66 93...
      | (?P<p1>0[1-9]\d)                         # 093...
    )
    (?P<sep>[-\x20]?)
    (?P<p2>\d{3})
    (?P=sep)
    (?P<last4>\d{4})
    (?![\d-])
    """,
    re.VERBOSE,
)


def mask(m: re.Match) -> str:
    """Return e.g. 'XXX-XXX-7894' or '+66 XX-XXX-7894'."""
    whole = m.group(0)
    prefix = m["intl"] or ""
    body = whole[len(prefix):-4]
    return prefix + re.sub(r"\d", "X", body) + m["last4"]


RULE = Rule(
    key="phone", label_th="เบอร์โทรศัพท์", label_en="Phone number",
    color="#f59e0b", weight=2, pattern=PATTERN, replace=mask,
    example="093-245-7894",
    explain_th=[
        "(?:\\+66…|0[1-9]\\d) — alternation รองรับทั้งรูปแบบไทยและ +66",
        "(?P=sep) — ตัวคั่นต้องสม่ำเสมอ ('-', ' ' หรือไม่มี)",
        "re.sub(r'\\d', 'X', …) — แทนทุกหลัก ยกเว้น 4 ตัวท้าย",
    ],
    explain_en=[
        '(?:\\+66…|0[1-9]\\d) — alternation covers both Thai and +66 formats',
        "(?P=sep) — the separator must be consistent ('-', ' ' or none)",
        "re.sub(r'\\d', 'X', …) — replaces every digit except the last 4",
    ],
)