#68010544 นาย ธีรปรัชญญ์ ตั้นพันธุ์
from __future__ import annotations

import re

from pdpa_shield.engine.types import Rule

# TODO(M06)
PATTERN: re.Pattern | None = None


def mask(m: re.Match) -> str:
    """Return the replacement for the `house` group only, i.e. 'XXX'."""
    raise NotImplementedError("M06: implement rules.address.mask")


RULE = Rule(
    key="address", label_th="ที่อยู่ (เลขที่บ้าน)", label_en="Address (house number)",
    color="#12b76a", weight=3, pattern=PATTERN, replace=mask, target="house",
    example="Address: 689 ซอยลาดกระบัง 19 ถนนลาดกระบัง แขวงลาดกระบัง เขตลาดกระบัง กรุงเทพฯ",
    explain_th=[],  # TODO(M06)
    explain_en=[],  # TODO(M06)
)