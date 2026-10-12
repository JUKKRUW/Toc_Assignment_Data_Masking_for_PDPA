"""Canonical acceptance cases — shared by pytest AND the Test Suite page (/api/tests).
Owner: M01. Rule owners add cases for their own rule through a PR.

Each case: (category, negative, name_th, name_en, input, expected)
negative=True means "must NOT be masked" (false-positive guard).
"""
CASES: list[tuple[str, bool, str, str, str, str]] = [
    ("card", False, "ตัวอย่างโจทย์", "Assignment example", "1234-5678-9012-3456", "XXXX-XXXX-XXXX-3456"),
    ("card", False, "คั่นด้วยช่องว่าง", "Space separator", "card=1234 5678 9012 3456", "card=XXXX XXXX XXXX 3456"),
    ("card", False, "ไม่มีตัวคั่น", "No separator", "card=4111111111111111", "card=XXXXXXXXXXXX1111"),
    ("card", True, "Transaction ID 20 หลัก", "20-digit transaction ID", "TXN=12345678901234567890", "TXN=12345678901234567890"),
    ("card", True, "ตัวคั่นไม่สม่ำเสมอ", "Inconsistent separators", "ref 1234-5678 9012-3456", "ref 1234-5678 9012-3456"),
    ("email", False, "ตัวอย่างโจทย์", "Assignment example", "somchai.d@company.com", "s*******d@company.com"),
    ("email", False, "โดเมน .co.th", ".co.th domain", "mail: a.b_c@bank.co.th", "mail: a***c@bank.co.th"),
    ("email", False, "มี + ใน username", "+ in username", "<nok+alert@gmail.com>", "<n*******t@gmail.com>"),
    ("email", True, "ไม่มี TLD", "No TLD", "user@localhost", "user@localhost"),
    ("phone", False, "ตัวอย่างโจทย์", "Assignment example", "093-245-7894", "XXX-XXX-7894"),
    ("phone", False, "ไม่มีตัวคั่น", "No separator", "tel:0812345678", "tel:XXXXXX5678"),
    ("phone", False, "รูปแบบ +66", "+66 format", "+66 93-245-7894", "+66 XX-XXX-7894"),
    ("phone", True, "ไม่ขึ้นต้นด้วย 0", "Does not start with 0", "code 123-456-7890", "code 123-456-7890"),
    ("phone", True, "หลักเกิน", "Too many digits", "ref 093-245-78945", "ref 093-245-78945"),
    ("dob", False, "ตัวอย่างโจทย์", "Assignment example", "DOB:25/12/2549", "DOB:XX/XX/25XX"),
    ("dob", False, "มีช่องว่าง + ตัวคั่น -", "Spaces and '-' separator", "dob : 01-01-2530", "dob : XX-XX-25XX"),
    ("dob", True, "วันที่ 32 / เดือน 13", "Day 32 / month 13", "DOB:32/13/2549", "DOB:32/13/2549"),
    ("dob", True, "ปี ค.ศ.", "Gregorian year", "DOB:25/12/2006", "DOB:25/12/2006"),
    ("address", False, "ตัวอย่างโจทย์", "Assignment example",
     "Address: 689 ซอยลาดกระบัง 19 ถนนลาดกระบัง แขวงลาดกระบัง เขตลาดกระบัง กรุงเทพฯ",
     "Address: XXX ซอยลาดกระบัง 19 ถนนลาดกระบัง แขวงลาดกระบัง เขตลาดกระบัง กรุงเทพฯ"),
    ("address", False, "ไม่มีซอย + เลขที่มี /", "No soi, house number with /",
     "Address: 99/12 ถนนพระราม 4 แขวงปทุมวัน เขตปทุมวัน กรุงเทพมหานคร",
     "Address: XXX ถนนพระราม 4 แขวงปทุมวัน เขตปทุมวัน กรุงเทพมหานคร"),
    ("address", False, "ต่างจังหวัด (หมู่/ตำบล/อำเภอ)", "Provincial (moo / tambon / amphoe)",
     "Address: 45 หมู่ 3 ถนนพหลโยธิน ตำบลคลองหนึ่ง อำเภอคลองหลวง จังหวัดปทุมธานี",
     "Address: XXX หมู่ 3 ถนนพหลโยธิน ตำบลคลองหนึ่ง อำเภอคลองหลวง จังหวัดปทุมธานี"),
    ("address", True, "ที่อยู่ไม่ครบรูปแบบ", "Incomplete address", "Address: 689 ไม่ระบุ", "Address: 689 ไม่ระบุ"),
    ("mixed", True, "วันเวลา + IP ใน log", "Timestamp + IP in a log line",
     "2026-09-24 10:15:32 ip=192.168.100.200", "2026-09-24 10:15:32 ip=192.168.100.200"),
    ("mixed", False, "หลายประเภทในบรรทัดเดียว", "Several types on one line",
     "user=somchai.d@company.com card=1234-5678-9012-3456 tel=093-245-7894",
     "user=s*******d@company.com card=XXXX-XXXX-XXXX-3456 tel=XXX-XXX-7894"),
]


def cases_for(category: str) -> list[tuple[str, bool, str, str, str, str]]:
    return [c for c in CASES if c[0] == category]
