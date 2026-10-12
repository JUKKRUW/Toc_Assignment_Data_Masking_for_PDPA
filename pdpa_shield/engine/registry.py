"""Rule registry — ทะเบียนกฎ                                         Owner: M07

หน้าที่: รวมกฎ regex ของเพื่อนทั้ง 5 คน (M02–M06) มาไว้ในรายการเดียว
และ "ลำดับในรายการ" คือ "ลำดับความสำคัญ (priority)" ที่ scanner ใช้

    กฎที่อยู่ก่อน ได้สิทธิ์จับข้อความก่อน
    ถ้ากฎที่อยู่หลังไปจับข้อความตำแหน่งที่ทับกัน -> ถูกข้าม (ดู scanner.py)

ทำไมต้องเรียงแบบนี้
    card  ก่อน phone : ตัวเลขข้างในเลขบัตรเครดิต ต้องไม่ถูกอ่านเป็นเบอร์โทร
    email ก่อน phone : ชื่ออีเมลที่เป็นตัวเลข เช่น 0812345678@mail.com
                       ถ้า email มาก่อน -> 0********8@mail.com      (ถูก: เซ็นเซอร์แบบอีเมล)
                       ถ้า phone มาก่อน -> XXXXXX5678@mail.com      (ผิด: โดนอ่านเป็นเบอร์โทร)
"""
from __future__ import annotations

from pdpa_shield.engine.types import Rule

# ดึงกฎของเพื่อนแต่ละคนเข้ามา (แต่ละไฟล์มีตัวแปร RULE อยู่ 1 ตัว)
# ชื่อในบรรทัดนี้ = ชื่อไฟล์ใน pdpa_shield/rules/   เช่น date -> rules/date.py
# หมายเหตุ: ไฟล์วันเกิดของกลุ่มเราชื่อ date.py (ต้นแบบใน zip ชื่อ dob.py)
#           แต่ key ของกฎข้างในยังเป็น "dob" เหมือนเดิม API และหน้าเว็บจึงไม่ต้องแก้อะไร
from pdpa_shield.rules import address, card, date, email, phone

# รายการกฎ เรียงตามความสำคัญ: บัตร -> อีเมล -> เบอร์โทร -> วันเกิด -> ที่อยู่
RULES: list[Rule] = [card.RULE, email.RULE, phone.RULE, date.RULE, address.RULE]

# ตารางหากฎจากชื่อ เช่น RULE_MAP["phone"] -> กฎเบอร์โทร   (API ของ M08 ใช้)
RULE_MAP: dict[str, Rule] = {r.key: r for r in RULES}

# รายชื่อกฎตามลำดับ ["card", "email", "phone", "dob", "address"]   (หน้าเว็บใช้ทำปุ่มเปิด/ปิดกฎ)
RULE_KEYS: list[str] = [r.key for r in RULES]
