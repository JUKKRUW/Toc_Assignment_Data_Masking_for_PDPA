"""Fake banking-log generator (random data only — never real customers).   Owner: M08

generate(n, seed) must return exactly n lines (each ending with "\\n") like:
    2026-09-24 08:01:00 [INFO ] LOGIN         session=685931 | email=... | card=...
Requirements
    [ ] 1–3 PII fields per line drawn from: email, card (all 3 separator styles), phone
        (dash / space / none / +66), "customer DOB:dd/mm/25yy", Thai address (Bangkok and
        provincial formats, with and without soi / moo).
    [ ] each PII field is MALFORMED with probability error_rate (default 25%): typo'd card,
        short phone, email without TLD, DOB 32/13, address without road ... These must not
        be masked and must be reported by engine/validate.py.
    [ ] ~35% of lines also contain a DECOY that is not personal data at all: 20-digit txn_id,
        IP address, "ref=123-456-7890", "order=1234-5678", amounts.
    [ ] Same seed -> same output (use random.Random(seed), not the global random).
    [ ] Timestamps increase line by line.

Acceptance tests: tests/test_loggen.py
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Optional

DECOY_EXAMPLES = [
    "txn_id=12345678901234567890",
    "ip=10.2.33.14",
    "ref=123-456-7890",
    "order=1234-5678",
]


_rng = random.Random()

FIRST = ["somchai", "somsri", "malee", "anan", "pim", "kittipong", "nok", "wichai", "suda", "arthit"]
LAST = ["d", "k", "srisuk", "wong", "p", "chai", "r", "t"]
DOMAINS = ["company.com", "bank.co.th", "gmail.com", "hotmail.com", "ku.ac.th", "mail.go.th"]
BKK = [("ลาดกระบัง", "ลาดกระบัง"), ("ปทุมวัน", "ปทุมวัน"), ("จตุจักร", "จตุจักร"), ("บางรัก", "สีลม")]
ROADS = ["ลาดกระบัง", "พหลโยธิน", "สุขุมวิท", "พระราม 4", "รัชดาภิเษก", "งามวงศ์วาน"]
UPC = [("คลองหนึ่ง", "คลองหลวง", "ปทุมธานี"), ("สุเทพ", "เมืองเชียงใหม่", "เชียงใหม่"),
       ("ในเมือง", "เมืองขอนแก่น", "ขอนแก่น")]
LEVELS = ["INFO", "INFO", "INFO", "WARN", "DEBUG", "ERROR"]
EVENTS = ["LOGIN", "TRANSFER", "PAYMENT", "KYC_UPDATE", "CARD_ACTIVATE", "OTP_SENT"]


def _d(n):
    return "".join(_rng.choice("0123456789") for _ in range(n))


def card():
    sep = _rng.choice(["-", "-", "-", " ", ""])
    return sep.join(_d(4) for _ in range(4))


def email():
    return f"{_rng.choice(FIRST)}{_rng.choice(['.', '_', ''])}{_rng.choice(LAST)}@{_rng.choice(DOMAINS)}"


def phone():
    p = "0" + _rng.choice("689") + _d(1)
    fmt = _rng.choice(["dash", "dash", "space", "none", "intl"])
    if fmt == "intl":
        return f"+66 {p[1:]}-{_d(3)}-{_d(4)}"
    sep = {"dash": "-", "space": " ", "none": ""}[fmt]
    return f"{p}{sep}{_d(3)}{sep}{_d(4)}"


def dob():
    return f"DOB:{_rng.randint(1, 28):02d}/{_rng.randint(1, 12):02d}/25{_rng.randint(10, 60)}"


def address():
    house = _rng.choice([str(_rng.randint(1, 999)), f"{_rng.randint(1, 199)}/{_rng.randint(1, 99)}"])
    if _rng.random() < 0.6:
        sub, dist = _rng.choice(BKK)
        soi = f"ซอย{_rng.choice(ROADS).split()[0]} {_rng.randint(1, 60)} " if _rng.random() < 0.6 else ""
        return f"Address: {house} {soi}ถนน{_rng.choice(ROADS)} แขวง{sub} เขต{dist} กรุงเทพฯ"
    t, a, p = _rng.choice(UPC)
    return f"Address: {house} หมู่ {_rng.randint(1, 12)} ถนน{_rng.choice(ROADS)} ตำบล{t} อำเภอ{a} จังหวัด{p}"


# ---------------------------------------------------------------------------
# Malformed values: look like personal data but break the format on purpose.
# The masking rules must NOT mask them; engine/validate.py must report them.
# ---------------------------------------------------------------------------
TYPO_CHARS = "OIlSBฟกดอ"


def bad_card():
    groups = [_d(4) for _ in range(4)]
    kind = _rng.choice(["typo", "short", "long", "mixed"])
    if kind == "typo":                       # a letter instead of a digit
        g = _rng.randrange(4)
        i = _rng.randrange(4)
        groups[g] = groups[g][:i] + _rng.choice(TYPO_CHARS) + groups[g][i + 1:]
        return "-".join(groups)
    if kind == "short":                      # one digit missing
        g = _rng.randrange(4)
        groups[g] = groups[g][:3]
        return "-".join(groups)
    if kind == "long":                       # one digit too many
        g = _rng.randrange(4)
        groups[g] += _d(1)
        return "-".join(groups)
    return f"{groups[0]}-{groups[1]} {groups[2]}-{groups[3]}"   # mixed separators


def bad_phone():
    kind = _rng.choice(["short", "long", "prefix", "typo"])
    p = "0" + _rng.choice("689") + _d(1)
    if kind == "short":
        return f"{p}-{_d(3)}-{_d(3)}"
    if kind == "long":
        return f"{p}-{_d(3)}-{_d(5)}"
    if kind == "prefix":
        return f"{_rng.choice('123456789')}{p[1:]}-{_d(3)}-{_d(4)}"
    return f"{p[:2]}{_rng.choice('OIlS')}-{_d(3)}-{_d(4)}"


def bad_email():
    user = f"{_rng.choice(FIRST)}{_rng.choice(['.', '_', ''])}{_rng.choice(LAST)}"
    domain = _rng.choice(DOMAINS)
    kind = _rng.choice(["no_tld", "double_at", "no_user"])
    if kind == "no_tld":
        return f"{user}@{domain.split('.')[0]}"
    if kind == "double_at":
        return f"{user}@@{domain}"
    return f"@{domain}"


def bad_dob():
    d, m, y = _rng.randint(1, 28), _rng.randint(1, 12), 2500 + _rng.randint(10, 60)
    kind = _rng.choice(["day", "month", "gregorian", "one_digit"])
    if kind == "day":
        return f"DOB:{_rng.randint(32, 39)}/{m:02d}/{y}"
    if kind == "month":
        return f"DOB:{d:02d}/{_rng.randint(13, 19)}/{y}"
    if kind == "gregorian":
        return f"DOB:{d:02d}/{m:02d}/{y - 543}"
    return f"DOB:{_rng.randint(1, 9)}/{_rng.randint(1, 9)}/{y}"


def bad_address():
    sub, dist = _rng.choice(BKK)
    road = _rng.choice(ROADS)
    house = str(_rng.randint(1, 999))
    kind = _rng.choice(["no_house", "no_road", "no_district", "unknown"])
    if kind == "no_house":
        return f"Address: ถนน{road} แขวง{sub} เขต{dist} กรุงเทพฯ"
    if kind == "no_road":
        return f"Address: {house} ซอย{road.split()[0]} {_rng.randint(1, 60)} แขวง{sub} เขต{dist} กรุงเทพฯ"
    if kind == "no_district":
        return f"Address: {house} ถนน{road} แขวง{sub} กรุงเทพฯ"
    return "Address: ไม่ระบุ"


# Decoys: NOT personal data at all — must be neither masked nor reported.
DECOYS = [
    lambda: f"txn_id={_d(20)}",
    lambda: f"ip=10.{_rng.randint(0, 255)}.{_rng.randint(0, 255)}.{_rng.randint(0, 255)}",
    lambda: f"ref={_rng.randint(100, 999)}-{_d(3)}-{_d(4)}",
    lambda: f"order={_d(4)}-{_d(4)}",
    lambda: f"amount={_rng.randint(100, 99999)}.{_d(2)} THB",
]

FIELDS = [
    (lambda: f"email={email()}", lambda: f"email={bad_email()}"),
    (lambda: f"card={card()}", lambda: f"card={bad_card()}"),
    (lambda: f"tel={phone()}", lambda: f"tel={bad_phone()}"),
    (lambda: f"customer {dob()}", lambda: f"customer {bad_dob()}"),
    (address, bad_address),
]


def generate(n: int = 25, seed: Optional[int] = None, error_rate: float = 0.25) -> str:
    """Return `n` fake log lines.

    Every personal-data field is malformed with probability `error_rate`, so a log
    contains a random mix of correct values (masked) and broken ones (reported as errors).
    With `seed=None` every call is different and timestamps start from the current time;
    with a seed the output is reproducible (used by the tests).
    """
    global _rng
    _rng = random.Random(seed)
    t = datetime(2026, 9, 24, 8, 0, 0) if seed is not None else datetime.now().replace(microsecond=0)
    lines = []
    for _ in range(n):
        t += timedelta(seconds=_rng.randint(1, 240))
        lvl, ev = _rng.choice(LEVELS), _rng.choice(EVENTS)
        fields = [f"session={_d(6)}"]
        for good, bad in _rng.sample(FIELDS, k=_rng.randint(1, 3)):
            fields.append((bad if _rng.random() < error_rate else good)())
        if _rng.random() < 0.35:
            fields.append(_rng.choice(DECOYS)())
        lines.append(f"{t:%Y-%m-%d %H:%M:%S} [{lvl:<5}] {ev:<13} " + " | ".join(fields))
    return "\n".join(lines) + "\n"