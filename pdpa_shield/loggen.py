from __future__ import annotations

from typing import Optional

DECOY_EXAMPLES = [
    "txn_id=12345678901234567890",
    "ip=10.2.33.14",
    "legacy_dob=DOB:32/13/2549",
    "ref=123-456-7890",
    "Address: ไม่ระบุ",
]


def generate(n: int = 25, seed: Optional[int] = None) -> str:
    raise NotImplementedError("M08: implement loggen.generate")
