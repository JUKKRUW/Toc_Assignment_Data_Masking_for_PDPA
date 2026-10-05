r"""Rule 02 — Email address  By : 68010585 นวมินทร์ ซอเซ็น

Spec (assignment)
    Hide the username except first and last character, keep the domain.
    somchai.d@company.com  ->  s*******d@company.com      (one * per hidden character)
"""
from __future__ import annotations

import re

from pdpa_shield.engine.types import Rule

PATTERN: re.Pattern | None = None


def mask(m: re.Match) -> str:
    """Return e.g. 's*******d@company.com'."""
    raise NotImplementedError("M03: implement rules.email.mask")


RULE = Rule(
    key="email", label_th="อีเมล", label_en="Email",
    color="#0a6cff", weight=1, pattern=PATTERN, replace=mask,
    example="somchai.d@company.com",
    explain_th=[],
    explain_en=[],
)
