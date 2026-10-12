"""Framework-free service layer.

The same functions back two runtimes:
    * the Flask API (pdpa_shield/app.py) when you run the server locally, and
    * the static GitHub Pages build, where they run in the browser through Pyodide
      (Python compiled to WebAssembly) — so masking still uses Python's `re`, and the
      log never leaves the visitor's machine.

Every function returns plain JSON-serialisable data; the `*_json` helpers return a JSON
string, which is the cheapest way to hand results to JavaScript from Pyodide.
"""
from __future__ import annotations

import json
import re
import textwrap
from typing import Iterable, Optional

from pdpa_shield.cases import CASES
from pdpa_shield.engine import registry
from pdpa_shield.engine.highlight import highlight_pattern
from pdpa_shield.engine.risk import stats
from pdpa_shield.engine.scanner import mask_text, scan
from pdpa_shield.engine.validate import find_issues
from pdpa_shield.loggen import generate

ENCODINGS = ("utf-8", "utf-8-sig", "cp874", "tis-620")
MAX_UPLOAD = 5 * 1024 * 1024


def mask(text: str, enabled: Optional[Iterable[str]] = None) -> dict:
    enabled = list(enabled) if enabled is not None else registry.RULE_KEYS
    parts = scan(text, registry.RULES, enabled)
    return {
        "parts": parts,
        "masked": "".join(p["masked"] if p["kind"] == "pii" else p["text"] for p in parts),
        "stats": stats(parts, registry.RULES),
        "issues": find_issues(text, {r.key: r.pattern for r in registry.RULES}, enabled),
    }


def decode_upload(raw: bytes) -> Optional[str]:
    """Decode an uploaded log; None if the size or encoding is not acceptable."""
    if len(raw) > MAX_UPLOAD:
        return None
    for enc in ENCODINGS:
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return None


def generate_log(n: int = 25) -> dict:
    return {"text": generate(max(5, min(int(n), 200)))}


def rules() -> list[dict]:
    out = []
    for r in registry.RULES:
        pat = r.pattern.pattern if r.pattern else ""
        flags = [n for n, v in (("VERBOSE", re.VERBOSE), ("IGNORECASE", re.IGNORECASE)) if r.pattern and r.pattern.flags & v]
        out.append({
            "key": r.key, "label": r.label_th, "label_en": r.label_en, "color": r.color, "weight": r.weight,
            "pattern": pat, "flags": flags, "target": r.target,
            "explain": r.explain_th, "explain_en": r.explain_en,
            "example": r.example, "example_masked": mask_text(r.example, [r]),
            "groups": list(r.pattern.groupindex) if r.pattern else [],
            "tokens": highlight_pattern(textwrap.dedent(pat).strip()),
        })
    return out


def tests() -> list[dict]:
    rows = []
    for cat, neg, th, en, inp, expected in CASES:
        actual = mask_text(inp, registry.RULES)
        rows.append({"category": cat, "name_th": th, "name_en": en, "negative": neg, "input": inp,
                     "expected": expected, "actual": actual, "passed": actual == expected})
    return rows


# ---- JSON bridges for Pyodide ---------------------------------------------------------
def _dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


def mask_json(text: str, enabled_json: str = "null") -> str:
    return _dump(mask(text, json.loads(enabled_json)))


def upload_json(raw, name: str) -> str:
    """`raw` is bytes, or a Pyodide JsProxy of a Uint8Array (converted with to_bytes)."""
    data = raw.to_bytes() if hasattr(raw, "to_bytes") else bytes(raw)
    text = decode_upload(data)
    return _dump({"text": text, "name": name} if text is not None else {"error": "unsupported file"})


def generate_json(n: int = 25) -> str:
    return _dump(generate_log(n))


def rules_json() -> str:
    return _dump(rules())


def tests_json() -> str:
    return _dump(tests())
