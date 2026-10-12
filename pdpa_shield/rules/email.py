r"""Rule 02 — Email address  By : 68010585 นวมินทร์ ซอเซ็น

Spec (assignment)
    Hide the username except first and last character, keep the domain.
    somchai.d@company.com  ->  s*******d@company.com      (one * per hidden character)
"""
from __future__ import annotations

import re

from pdpa_shield.engine.types import Rule

PATTERN: re.Pattern | None = re.compile(
    r"""
    (?<![A-Za-z0-9._%+-])               # ไม่ต่อจากตัวอักษรของอีเมลอื่น
    (?P<first>[A-Za-z0-9])              # ตัวแรก (เปิดเผย)
    (?:
        (?P<middle>[A-Za-z0-9._%+-]*)   # ส่วนกลาง (ซ่อน)
        (?P<last>[A-Za-z0-9])           # ตัวสุดท้าย (เปิดเผย)
    )?
    @
    (?P<domain>
        (?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+   # sub-domain.
        [A-Za-z]{2,}                                      # TLD
    )
    (?![A-Za-z0-9-])
    """,
    re.VERBOSE,
)


def mask(m: re.Match) -> str:
    """Return e.g. 's*******d@company.com'. A 1-char username is left as is."""
    middle = m["middle"] or ""
    return f"{m['first']}{'*' * len(middle)}{m['last'] or ''}@{m['domain']}"


RULE = Rule(
    key="email", label_th="อีเมล", label_en="Email",
    color="#0a6cff", weight=1, pattern=PATTERN, replace=mask,
    example="somchai.d@company.com",
    explain_th=[
        "(?P<first>…) / (?P<last>…) — เก็บตัวแรกและตัวสุดท้ายของ username",
        "(?P<middle>[A-Za-z0-9._%+-]*) — ส่วนที่ถูกแทนด้วย * ตามจำนวนตัวอักษร",
        "(?:sub\\.)+TLD — quantifier + ซ้อนกลุ่ม รองรับโดเมนหลายระดับ เช่น .co.th",
    ],
    explain_en=[
        '(?P<first>…) / (?P<last>…) — keep the first and last characters of the username',
        '(?P<middle>[A-Za-z0-9._%+-]*) — replaced with one * per character',
        '(?:sub\\.)+TLD — a quantified nested group handles multi-level domains such as .co.th',
    ],
)
