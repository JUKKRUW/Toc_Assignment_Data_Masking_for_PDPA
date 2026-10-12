r"""Rule 01 — Credit card number.                                  Owner: M02

Spec (assignment)
    Format XXXX-XXXX-XXXX-XXXX, keep only the last 4 digits.
    1234-5678-9012-3456  ->  XXXX-XXXX-XXXX-3456

Requirements
    [ ] Separator may be "-", a single space, or nothing — but the SAME one throughout.
        Hint: a named group for the separator + a backreference (?P=sep).
    [ ] Must NOT match inside a longer digit run (e.g. a 20-digit transaction id).
        Hint: negative lookbehind / lookahead.
    [ ] Keep the original separator in the output.
    [ ] Expose a named group `last4`.
    [ ] Write the pattern with re.VERBOSE and a comment on every line.
    [ ] Fill in explain_th / explain_en (format: "<regex piece> — <what it does>").
Nice to have
    [ ] info(): return "luhn_ok" / "luhn_fail" using the Luhn checksum.

Acceptance tests: tests/rules/test_card.py
"""
from __future__ import annotations

import re

from pdpa_shield.engine.types import Rule

PATTERN: re.Pattern | None = re.compile(
    r"""
    (?<![\d-])              # ด้านหน้าต้องไม่ใช่ตัวเลขหรือขีด
    (?P<g1>\d{4})
    (?P<sep>[-\x20]?)       # ตัวคั่น: '-' / ' ' / ไม่มี
    (?P<g2>\d{4})
    (?P=sep)                # backreference → ตัวคั่นเดิม
    (?P<g3>\d{4})
    (?P=sep)
    (?P<last4>\d{4})
    (?![\d-])               # ด้านหลังต้องไม่ใช่ตัวเลขหรือขีด
    """,
    re.VERBOSE,
)


def mask(m: re.Match) -> str:
    """Return the masked text for the whole match, e.g. 'XXXX-XXXX-XXXX-3456'."""
    s = m["sep"]
    return f"XXXX{s}XXXX{s}XXXX{s}{m['last4']}"


def info(m: re.Match) -> str | None:
    """Luhn checksum shown in the tooltip (not used for matching)."""
    digits = re.sub(r"\D", "", m.group(0))
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d = d * 2 - 9 if d * 2 > 9 else d * 2
        total += d
    return "luhn_ok" if total % 10 == 0 else "luhn_fail"


RULE = Rule(
    key="card", label_th="เลขบัตรเครดิต", label_en="Credit card number",
    color="#ef4444", weight=5, pattern=PATTERN, replace=mask, info=info,
    example="1234-5678-9012-3456",
    explain_th=[
        "(?<![\\d-]) / (?![\\d-]) — lookaround กันจับกลางเลขที่ยาวกว่า 16 หลัก",
        "(?P<sep>[-\\x20]?) + (?P=sep) — backreference บังคับตัวคั่นเดียวกันทั้งเลข",
        "(?P<last4>\\d{4}) — named group เก็บ 4 ตัวท้ายไว้แสดง",
    ],
    explain_en=[
        '(?<![\\d-]) / (?![\\d-]) — lookarounds stop matches inside numbers longer than 16 digits',
        '(?P<sep>[-\\x20]?) + (?P=sep) — a backreference forces one separator throughout',
        '(?P<last4>\\d{4}) — a named group keeps the last 4 digits visible',
    ],
)