# 68010544 ธีรปรัชญ์ ตั้นพันธุ์
from __future__ import annotations

import re

from pdpa_shield.engine.types import Rule

PATTERN: re.Pattern | None = re.compile(
    r"""
    (?P<prefix>(?<![A-Za-z])Address[\t\x20]*:[\t\x20]*)
    (?P<house>\d{1,5}(?:/\d{1,5})?)                                   # 689 หรือ 99/12
    [\t\x20]+
    (?:(?P<moo>(?:หมู่(?:ที่)?|ม\.)[\t\x20]*\d{1,3})[\t\x20]+)?         # หมู่ (optional)
    (?:(?P<soi>(?:ซอย|ซ\.)[\t\x20]*\S+(?:[\t\x20]+\d+(?:/\d+)?)?)[\t\x20]+)?  # ซอย (optional)
    (?P<road>(?:ถนน|ถ\.)[\t\x20]*\S+(?:[\t\x20]+\d+)?)                 # ถนน
    [\t\x20]+
    (?P<subdistrict>(?:แขวง|ตำบล|ต\.)[\t\x20]*\S+)                     # แขวง / ตำบล
    [\t\x20]+
    (?P<district>(?:เขต|อำเภอ|อ\.)[\t\x20]*\S+)                        # เขต / อำเภอ
    [\t\x20]+
    (?P<province>(?:จังหวัด|จ\.)?[\t\x20]*[^\s,;|]+)                   # จังหวัด
    """,
    re.VERBOSE,
)


def mask(m: re.Match) -> str:
    """Return the replacement for the `house` group only, i.e. 'XXX'."""
    return "XXX"


RULE = Rule(
    key="address", label_th="ที่อยู่ (เลขที่บ้าน)", label_en="Address (house number)",
    color="#12b76a", weight=3, pattern=PATTERN, replace=mask, target="house",
    example="Address: 689 ซอยลาดกระบัง 19 ถนนลาดกระบัง แขวงลาดกระบัง เขตลาดกระบัง กรุงเทพฯ",
    explain_th=[
        "Named groups: house / moo / soi / road / subdistrict / district / province",
        "(…)? — หมู่ และ ซอย เป็น optional",
        "(?:แขวง|ตำบล) / (?:เขต|อำเภอ) — รองรับทั้ง กทม. และต่างจังหวัด",
        "เซ็นเซอร์เฉพาะ span ของ group 'house'",
    ],
    explain_en=[
        'Named groups: house / moo / soi / road / subdistrict / district / province',
        '(…)? — moo and soi are optional',
        '(?:แขวง|ตำบล) / (?:เขต|อำเภอ) — supports Bangkok and provincial addresses',
        "Masks only the span of group 'house'",
    ],
)
