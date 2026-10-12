"""Shared contracts used by every module.  Owner: M01 (Tech Lead) — change only via PR review.

These types are the "interface" that lets 10 people work in parallel:
    * rule owners (M02–M06) only fill in ONE `Rule` each,
    * the engine owner (M07) consumes `Rule` objects without knowing which rule is which,
    * the API owner (M08) serialises `Part` / `Stats` dicts to JSON,
    * the frontend owners (M09, M10) read that JSON (see docs/API.md).

Only the standard-library `re` module may be used for matching.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Literal, Optional, TypedDict, Union

RuleKey = Literal["card", "email", "phone", "dob", "address"]


@dataclass(frozen=True)
class Rule:
    """One masking rule.

    key         stable id used by the API and the frontend
    label_th    UI label in Thai          label_en   UI label in English
    color       hex colour used for highlights in the UI
    weight      risk weight used by the PDPA Risk Score (engine/risk.py)
    pattern     compiled `re` pattern, or None while the rule is not implemented yet
    replace     function(match) -> replacement text for the *target* span
    target      0 = replace the whole match, or the name of a group to replace only that group
    example     one input string shown on the Rules page
    explain_th / explain_en   bullet lines "code — description" shown on the Rules page
    info        optional function(match) -> i18n key shown in the tooltip (e.g. "luhn_ok")
    """

    key: RuleKey
    label_th: str
    label_en: str
    color: str
    weight: int
    pattern: Optional[re.Pattern]
    replace: Callable[[re.Match], str]
    target: Union[int, str] = 0
    example: str = ""
    explain_th: list[str] = field(default_factory=list)
    explain_en: list[str] = field(default_factory=list)
    info: Optional[Callable[[re.Match], Optional[str]]] = None


class TextPart(TypedDict):
    kind: Literal["text"]
    text: str


class PiiPart(TypedDict):
    kind: Literal["pii"]
    rule: RuleKey
    original: str          # text of the target span before masking
    masked: str            # replacement text
    match: str             # full match text (group 0)
    groups: dict[str, str]  # named groups that matched (None values removed)
    info: Optional[str]    # i18n key or None


Part = Union[TextPart, PiiPart]


class Stats(TypedDict):
    counts: dict[str, int]    # per rule key
    total: int
    risk: int                 # 0..100
    level: str                # Thai label: "ไม่พบ" | "ต่ำ" | "กลาง" | "สูง"
    level_code: Literal["none", "low", "mid", "high"]


def require_pattern(rule: Rule) -> re.Pattern:
    """Raise NotImplementedError until the rule owner has written a pattern.

    Tests that hit NotImplementedError are reported as XFAIL ("not implemented yet"),
    so CI stays green while the team is still working.
    """
    if rule.pattern is None:
        raise NotImplementedError(f"rule '{rule.key}' has no pattern yet")
    return rule.pattern


def apply_single(rule: Rule, text: str) -> str:
    """Apply ONE rule to `text` with re.sub (no priority / overlap handling).

    Rule owners use this to test their rule in isolation, without waiting for the engine (M07).
    """
    pattern = require_pattern(rule)

    def _repl(m: re.Match) -> str:
        if rule.target == 0:
            return rule.replace(m)
        s, e = m.span(rule.target)
        whole, base = m.group(0), m.start()
        return whole[: s - base] + rule.replace(m) + whole[e - base:]

    return pattern.sub(_repl, text)
