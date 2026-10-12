"""Benchmark ของ M07 — เซ็นเซอร์ log 10,000 บรรทัด ต้องเสร็จภายใน 2 วินาที

วิธีรัน (ที่โฟลเดอร์บนสุดของโปรเจกต์):
    python scripts/benchmark_engine.py
    python scripts/benchmark_engine.py 50000      # ลองจำนวนบรรทัดอื่น

ผลที่ได้ให้จดลงรายงานส่วนของ M07
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ให้ import pdpa_shield ได้เมื่อรันจาก scripts/

from pdpa_shield.engine import registry, risk, scanner  # noqa: E402

LIMIT_SECONDS = 2.0

# ใช้ตอนที่ loggen ของ M08 ยังไม่เสร็จ: บรรทัด log ตัวอย่างที่มีข้อมูลส่วนบุคคลครบ 5 แบบ
SAMPLE_LINES = [
    "2026-10-08 09:15:02 INFO  txn=48213 card=1234-5678-9012-3456 status=OK",
    "2026-10-08 09:15:03 INFO  user=somchai.d@company.com login ok",
    "2026-10-08 09:15:04 WARN  callback tel=093-245-7894 retry=2",
    "2026-10-08 09:15:05 INFO  kyc DOB:25/12/2549 verified",
    "2026-10-08 09:15:06 INFO  Address: 689 ซอยลาดกระบัง 19 ถนนลาดกระบัง แขวงลาดกระบัง เขตลาดกระบัง กรุงเทพฯ",
    "2026-10-08 09:15:07 DEBUG heartbeat ok id=0000-1111 ref=12-34-56",
]


def make_log(n: int) -> str:
    """สร้าง log n บรรทัด — ใช้ loggen ของ M08 ถ้าเสร็จแล้ว ไม่งั้นใช้บรรทัดตัวอย่างข้างบน"""
    try:
        from pdpa_shield import loggen
        return loggen.generate(n, seed=42)
    except (ImportError, NotImplementedError):
        return "\n".join(SAMPLE_LINES[i % len(SAMPLE_LINES)] for i in range(n))


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10_000
    text = make_log(n)

    start = time.perf_counter()
    parts = scanner.scan(text, registry.RULES)                  # หา + ตัดชิ้น
    masked = "".join(p["masked"] if p["kind"] == "pii" else p["text"] for p in parts)
    result = risk.stats(parts, registry.RULES)                  # นับ + คิดคะแนน
    seconds = time.perf_counter() - start

    print(f"บรรทัด          : {len(text.splitlines()):,}")
    print(f"ขนาดข้อความ     : {len(text):,} ตัวอักษร")
    print(f"เจอข้อมูลส่วนตัว : {result['total']:,} จุด  {result['counts']}")
    print(f"เวลาที่ใช้       : {seconds:.3f} วินาที  (เกณฑ์ < {LIMIT_SECONDS} วินาที)")
    print("ผล             :", "ผ่าน" if seconds < LIMIT_SECONDS else "ไม่ผ่าน")
    assert len(masked) > 0


if __name__ == "__main__":
    main()
