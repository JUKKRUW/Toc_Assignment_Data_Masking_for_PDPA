#68010467 ธนภัทร แคล้วคลาด
r"""Rule 04 — Date of birth (starts with "DOB:").                  Owner: M05

Spec (assignment)
    Mask everything except the first 2 digits of the Buddhist-era year.
    DOB:25/12/2549  ->  DOB:XX/XX/25XX

"""
from __future__ import annotations

import re

from pdpa_shield.engine.types import Rule

PATTERN: re.Pattern | None = re.compile(
    r"""
    (?P<prefix>(?<![A-Za-z])DOB[\t\x20]*:[\t\x20]*)
    (?P<day>0[1-9]|[12]\d|3[01])
    (?P<sep>[/.-])
    (?P<month>0[1-9]|1[0-2])
    (?P=sep)
    (?P<century>25)            # 2 หลักแรกของปี พ.ศ.
    (?P<yy>\d{2})
    (?!\d)
    """,
    re.VERBOSE | re.IGNORECASE,
)


def mask(m: re.Match) -> str:
    """Return e.g. 'DOB:XX/XX/25XX'."""
    s = m["sep"]
    return f"{m['prefix']}XX{s}XX{s}{m['century']}XX"


RULE = Rule(
    key="dob", label_th="วันเดือนปีเกิด", label_en="Date of birth",
    color="#8b5cf6", weight=3, pattern=PATTERN, replace=mask,
    example="DOB:25/12/2549",
    explain_th=[
        "0[1-9]|[12]\\d|3[01] — ตรวจวันที่ 01–31",
        "0[1-9]|1[0-2] — ตรวจเดือน 01–12",
        "(?P<century>25)\\d{2} — ปี พ.ศ. 25xx เปิดเผยเฉพาะ 2 หลักแรก",
    ],
    explain_en=[
        '0[1-9]|[12]\\d|3[01] — validates day 01–31',
        '0[1-9]|1[0-2] — validates month 01–12',
        '(?P<century>25)\\d{2} — Buddhist-era year 25xx, only the first 2 digits stay visible',
    ],
)
