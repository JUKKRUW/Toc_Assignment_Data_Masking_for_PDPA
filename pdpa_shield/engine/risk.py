"""PDPA Risk Score — คะแนนความเสี่ยงของข้อความ                       Owner: M07

หน้าที่: นับว่าเจอข้อมูลส่วนบุคคลแต่ละประเภทกี่จุด แล้วคิดเป็นคะแนน 0–100

สูตร
    risk  = min(100, sum(จำนวนที่เจอ[กฎ] * น้ำหนัก[กฎ]) * 2)
    level = "high" ถ้า risk >= 60
            "mid"  ถ้า risk >= 25
            "low"  ถ้า risk > 0
            "none" ถ้าไม่เจออะไรเลย
    ชื่อระดับภาษาไทย: none="ไม่พบ", low="ต่ำ", mid="กลาง", high="สูง"

น้ำหนัก (weight) กำหนดไว้ในไฟล์กฎของเพื่อนแต่ละคน
    บัตร 5, อีเมล 1, เบอร์โทร 2, วันเกิด 3, ที่อยู่ 3   (บัตรเครดิตอันตรายที่สุด)

ตัวอย่าง: เจออย่างละ 1 จุด -> (5 + 1 + 2 + 3 + 3) * 2 = 28 -> ระดับ "กลาง"

ไฟล์ทดสอบ: tests/engine/test_risk.py
"""
from __future__ import annotations

from pdpa_shield.engine.types import Part, Rule, Stats

# ชื่อระดับความเสี่ยงภาษาไทย
LEVEL_TH = {"none": "ไม่พบ", "low": "ต่ำ", "mid": "กลาง", "high": "สูง"}


def stats(parts: list[Part], rules: list[Rule]) -> Stats:
    """นับชิ้น pii แยกตามกฎ (ทุกกฎต้องมีในผลลัพธ์ ถ้าไม่เจอให้เป็น 0) แล้วคิดคะแนน"""
    # 1) นับจำนวน: เริ่มทุกกฎที่ 0 แล้วบวกทีละชิ้นที่เป็น pii
    counts = {r.key: 0 for r in rules}
    for p in parts:
        if p["kind"] == "pii":
            counts[p["rule"]] = counts.get(p["rule"], 0) + 1

    # 2) คิดคะแนน: จำนวน x น้ำหนัก ของทุกกฎรวมกัน แล้วคูณ 2  และไม่เกิน 100
    weight = {r.key: r.weight for r in rules}
    risk = min(100, sum(weight.get(k, 0) * c for k, c in counts.items()) * 2)

    # 3) แปลงคะแนนเป็นระดับ
    code = "high" if risk >= 60 else "mid" if risk >= 25 else "low" if risk > 0 else "none"

    return {
        "counts": counts,                  # เช่น {"card": 1, "email": 0, ...}
        "total": sum(counts.values()),     # รวมทั้งหมดกี่จุด
        "risk": risk,                      # คะแนน 0–100
        "level": LEVEL_TH[code],           # ระดับภาษาไทย
        "level_code": code,                # ระดับภาษาอังกฤษ (หน้าเว็บใช้เลือกสี)
    }
