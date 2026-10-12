"""Input validation — find values that LOOK like personal data but are malformed.

The masking rules are strict on purpose (e.g. a card must be exactly 4-4-4-4 digits), so a
typo such as ``card=1234-ฟ123-2345-1536`` is not masked. That is correct per the spec, but in a
real log it would leak 15 digits of a card number. This module finds such values and explains
what is wrong, so the UI can show an error instead of silently passing them through.

Two ways a value becomes a candidate (both written with Python ``re``):
    1. Label-based  — a field that names the data type: ``card=…``, ``tel=…``, ``email=…``,
                      ``DOB:…``, ``Address: …``
    2. Shape-based  — four 3–5 character groups with at least 12 digits, e.g. ``1234-ฟ123-2345-1536``
                      even when there is no label.
A candidate is fine when the strict rule matches it; otherwise it becomes an Issue with a
human-readable reason in Thai and English.

Dependency-free on purpose: pass ``{rule_key: compiled_pattern}``.
"""
from __future__ import annotations

import re
from typing import Iterable, Optional, TypedDict

THAI = "฀-๿"


class Issue(TypedDict):
    rule: str
    start: int
    end: int
    text: str
    line: int
    reason_th: str
    reason_en: str


# ---------------------------------------------------------------------------
# Candidate finders
# ---------------------------------------------------------------------------
LABEL_RE = re.compile(
    r"""
    (?<![A-Za-z_])
    (?P<key>credit_card|card|tel|phone|mobile|e-mail|email|mail)   # field name
    [\t\x20]*[=:][\t\x20]*                                          # = or :
    (?P<value>[^|,;\n]*?)                                           # value (lazy)
    (?=[\t\x20]*(?:[|,;\n]|$)|[\t\x20]{2,})                          # up to a delimiter / 2 spaces
    """,
    re.VERBOSE | re.IGNORECASE | re.MULTILINE,
)
KEY_TO_RULE = {"credit_card": "card", "card": "card", "tel": "phone", "phone": "phone",
               "mobile": "phone", "e-mail": "email", "email": "email", "mail": "email"}

DOB_LABEL_RE = re.compile(r"(?<![A-Za-z])DOB[\t\x20]*:[\t\x20]*(?P<value>[^\s|,;]*)", re.IGNORECASE)

ADDRESS_LABEL_RE = re.compile(
    r"(?<![A-Za-z])Address[\t\x20]*:[\t\x20]*(?P<value>[^|\n]*?)(?=[\t\x20]*(?:\||\n|$))",
    re.MULTILINE,
)

CARD_SHAPE_RE = re.compile(
    rf"""
    (?<![\w-])
    (?P<value>
        (?:(?=[0-9A-Za-z{THAI}]{{0,4}}\d)[0-9A-Za-z{THAI}]{{3,5}}[-\x20]){{3}}  # 3 groups of 3-5 chars, each with a digit
        (?=[0-9A-Za-z{THAI}]{{0,4}}\d)[0-9A-Za-z{THAI}]{{3,5}}                  # last group
    )
    (?![\w-])
    """,
    re.VERBOSE,
)


# ---------------------------------------------------------------------------
# Diagnoses: explain WHY a candidate is not valid
# ---------------------------------------------------------------------------
def _bad_chars(value: str, allowed: str) -> list[str]:
    return sorted(set(re.findall(rf"[^{allowed}]", value)))


def diagnose_card(v: str) -> tuple[list[str], list[str]]:
    th, en = [], []
    bad = _bad_chars(v, r"\d\x20-")
    if bad:
        th.append("มีอักขระที่ไม่ใช่ตัวเลข: " + " ".join(bad))
        en.append("contains non-digit characters: " + " ".join(bad))
    digits = len(re.findall(r"\d", v))
    if digits != 16:
        th.append(f"มีตัวเลข {digits} หลัก ต้องมี 16 หลัก")
        en.append(f"has {digits} digits, needs 16")
    seps = set(re.findall(r"[-\x20]", v))
    if len(seps) > 1:
        th.append("ใช้ตัวคั่นปนกัน (- กับช่องว่าง)")
        en.append("mixes '-' and space separators")
    groups = [len(g) for g in re.split(r"[-\x20]+", v) if g]
    if seps and groups != [4, 4, 4, 4]:
        th.append("แต่ละช่วงต้องมี 4 ตัว พบ " + "-".join(map(str, groups)))
        en.append("each group needs 4 characters, found " + "-".join(map(str, groups)))
    return th, en


def diagnose_phone(v: str) -> tuple[list[str], list[str]]:
    th, en = [], []
    bad = _bad_chars(v, r"\d\x20+-")
    if bad:
        th.append("มีอักขระที่ไม่ใช่ตัวเลข: " + " ".join(bad))
        en.append("contains non-digit characters: " + " ".join(bad))
    intl = v.startswith("+66")
    digits = len(re.findall(r"\d", v[3:] if intl else v))
    need = 9 if intl else 10
    if not intl and not v.startswith("0"):
        th.append("ต้องขึ้นต้นด้วย 0 หรือ +66")
        en.append("must start with 0 or +66")
    if digits != need:
        th.append(f"มีตัวเลข {digits} หลัก ต้องมี {need} หลัก")
        en.append(f"has {digits} digits, needs {need}")
    if len(set(re.findall(r"(?<=\d)[-\x20](?=\d)", v))) > 1:
        th.append("ใช้ตัวคั่นปนกัน")
        en.append("mixes separators")
    return th, en


def diagnose_email(v: str) -> tuple[list[str], list[str]]:
    th, en = [], []
    if v.count("@") != 1:
        return ["ต้องมีเครื่องหมาย @ หนึ่งตัว"], ["needs exactly one @"]
    user, domain = v.split("@")
    if not user:
        th.append("ไม่มีชื่อผู้ใช้หน้า @")
        en.append("nothing before @")
    if not re.search(r"\.[A-Za-z]{2,}$", domain):
        th.append("โดเมนไม่มีนามสกุล เช่น .com หรือ .co.th")
        en.append("domain has no TLD such as .com or .co.th")
    bad = _bad_chars(v, r"A-Za-z0-9._%+@-")
    if bad:
        th.append("มีอักขระที่ใช้ในอีเมลไม่ได้: " + " ".join(bad))
        en.append("characters not allowed in an email: " + " ".join(bad))
    return th, en


def diagnose_dob(v: str) -> tuple[list[str], list[str]]:
    if not v:
        return ["ไม่มีวันที่หลัง DOB:"], ["no date after DOB:"]
    m = re.fullmatch(r"(?P<d>\d{1,2})(?P<s>[/.-])(?P<m>\d{1,2})(?P=s)(?P<y>\d{4})", v)
    if not m:
        return ["รูปแบบต้องเป็น วว/ดด/ปปปป (พ.ศ.)"], ["format must be DD/MM/YYYY (Buddhist era)"]
    th, en = [], []
    d, mo, y = int(m["d"]), int(m["m"]), int(m["y"])
    if not 1 <= d <= 31:
        th.append(f"วันที่ {m['d']} ไม่มีจริง")
        en.append(f"day {m['d']} does not exist")
    if not 1 <= mo <= 12:
        th.append(f"เดือน {m['m']} ไม่มีจริง")
        en.append(f"month {m['m']} does not exist")
    if not 2500 <= y <= 2599:
        th.append(f"ปี {y} ไม่ใช่ปี พ.ศ. 25xx")
        en.append(f"year {y} is not a Buddhist-era year 25xx")
    if len(m["d"]) != 2 or len(m["m"]) != 2:
        th.append("วันและเดือนต้องเป็นเลข 2 หลัก")
        en.append("day and month need 2 digits")
    return th, en


def diagnose_address(v: str) -> tuple[list[str], list[str]]:
    if not v:
        return ["ไม่มีที่อยู่หลัง Address:"], ["no address after Address:"]
    th, en = [], []
    if not re.match(r"\d{1,5}(?:/\d{1,5})?(?=[\t\x20]|$)", v):
        th.append("ต้องขึ้นต้นด้วยเลขที่บ้าน")
        en.append("must start with a house number")
    parts = [("ถนน", "road", r"ถนน|ถ\."), ("แขวง/ตำบล", "subdistrict", r"แขวง|ตำบล|ต\."),
             ("เขต/อำเภอ", "district", r"เขต|อำเภอ|อ\.")]
    missing = [(t, e) for t, e, pat in parts if not re.search(pat, v)]
    if missing:
        th.append("ขาด: " + ", ".join(t for t, _ in missing))
        en.append("missing: " + ", ".join(e for _, e in missing))
    return th, en


DIAGNOSE = {"card": diagnose_card, "phone": diagnose_phone, "email": diagnose_email,
            "dob": diagnose_dob, "address": diagnose_address}
FALLBACK = {
    "card": ("รูปแบบต้องเป็น XXXX-XXXX-XXXX-XXXX", "expected XXXX-XXXX-XXXX-XXXX"),
    "phone": ("รูปแบบต้องเป็น 0XX-XXX-XXXX", "expected 0XX-XXX-XXXX"),
    "email": ("รูปแบบอีเมลไม่ถูกต้อง", "not a valid email address"),
    "dob": ("รูปแบบวันเกิดไม่ถูกต้อง", "not a valid date of birth"),
    "address": ("ลำดับส่วนของที่อยู่ไม่ถูกต้อง", "address parts are not in the expected order"),
}


# ---------------------------------------------------------------------------
def find_issues(text: str, patterns: dict[str, Optional[re.Pattern]],
                enabled: Optional[Iterable[str]] = None) -> list[Issue]:
    """Return malformed personal-data values in `text`, sorted by position."""
    keys = set(enabled) if enabled is not None else set(patterns)
    strict = {k: [m.span() for m in p.finditer(text)] for k, p in patterns.items() if p is not None}

    def covered(rule: str, s: int, e: int) -> bool:
        spans = strict.get(rule)
        if spans is None:
            return True  # rule not implemented yet: nothing to compare with
        if rule == "address":
            return any(ms == s for ms, _ in spans)
        return any(ms <= s and me >= e for ms, me in spans)

    candidates: list[tuple[str, int, int, str]] = []   # rule, start, end, value
    for m in LABEL_RE.finditer(text):
        candidates.append((KEY_TO_RULE[m["key"].lower()], m.start("value"), m.end("value"), m["value"]))
    for m in DOB_LABEL_RE.finditer(text):
        candidates.append(("dob", m.start(), m.end("value"), m["value"]))
    for m in ADDRESS_LABEL_RE.finditer(text):
        candidates.append(("address", m.start(), m.end("value"), m["value"]))
    for m in CARD_SHAPE_RE.finditer(text):
        if len(re.findall(r"\d", m["value"])) >= 12:
            candidates.append(("card", m.start("value"), m.end("value"), m["value"]))

    issues: list[Issue] = []
    taken: list[tuple[int, int]] = []
    for rule, s, e, value in candidates:                 # label-based first, shape-based last
        if rule not in keys or s == e and rule not in ("dob", "address"):
            continue
        if covered(rule, s, e) or any(s < te and ts < e for ts, te in taken):
            continue
        th, en = DIAGNOSE[rule](value.strip())
        if not th:
            th, en = [FALLBACK[rule][0]], [FALLBACK[rule][1]]
        issues.append({"rule": rule, "start": s, "end": e, "text": text[s:e],
                       "line": text.count("\n", 0, s) + 1,
                       "reason_th": "; ".join(th), "reason_en": "; ".join(en)})
        taken.append((s, e))
    return sorted(issues, key=lambda i: i["start"])
