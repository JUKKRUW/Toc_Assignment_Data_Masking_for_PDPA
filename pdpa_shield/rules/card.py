r"""Rule 01 — Credit card number.                          

Spec (assignment)
    Format XXXX-XXXX-XXXX-XXXX, keep only the last 4 digits.
    1234-5678-9012-3456  ->  XXXX-XXXX-XXXX-3456

Requirements
    [ ] Separator may be "-", a single space, or nothing — but the SAME one throughout.
        Hint: a named group for the separator + a backreference (?P=sep).
    [ ] Must NOT match inside a longer digit run (e.g. a 20-digit transaction id).
        Hint: negative lookbehind / lookahead.
    [ ] Keep the original separator in the output.
    [ ] Expose a named group `last4`.
    [ ] Write the pattern with re.VERBOSE and a comment on every line.
    [ ] Fill in explain_th / explain_en (format: "<regex piece> — <what it does>").
Nice to have
    [ ] info(): return "luhn_ok" / "luhn_fail" using the Luhn checksum.

Acceptance tests: tests/rules/test_card.py
"""


from __future__ import annotations

import re

from pdpa_shield.engine.types import Rule

# TODO(M02): replace None with re.compile(r"""...""", re.VERBOSE)
PATTERN: re.Pattern | None = None


def mask(m: re.Match) -> str:
    """Return the masked text for the whole match, e.g. 'XXXX-XXXX-XXXX-3456'."""
    raise NotImplementedError("M02: implement rules.card.mask")


def info(m: re.Match) -> str | None:
    """Optional: return 'luhn_ok' or 'luhn_fail'. Return None to show nothing."""
    return None


RULE = Rule(
    key="card", label_th="เลขบัตรเครดิต", label_en="Credit card number",
    color="#ef4444", weight=5, pattern=PATTERN, replace=mask, info=info,
    example="1234-5678-9012-3456",
    explain_th=[],  # TODO(M02)
    explain_en=[],  # TODO(M02)
)
