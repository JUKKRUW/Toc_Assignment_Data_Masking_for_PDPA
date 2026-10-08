r"""Rule 04 — Date of birth By : 68010467 ธนภัทร แคล้วคลาด

"""
from __future__ import annotations

import re

from pdpa_shield.engine.types import Rule

# TODO(M05)
PATTERN: re.Pattern | None = None


def mask(m: re.Match) -> str:
    """Return e.g. 'DOB:XX/XX/25XX'."""
    raise NotImplementedError("M05: implement rules.dob.mask")


RULE = Rule(
    key="dob", label_th="วันเดือนปีเกิด", label_en="Date of birth",
    color="#8b5cf6", weight=3, pattern=PATTERN, replace=mask,
    example="DOB:25/12/2549",
    explain_th=[],  # TODO(M05)
    explain_en=[],  # TODO(M05)
)