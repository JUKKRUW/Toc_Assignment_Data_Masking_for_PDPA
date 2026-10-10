# HTTP API

*Owner: M08.* The frontend relies on these exact shapes. Changing a field = `contract` issue first.

## `POST /api/mask`

Request `{"text": "…", "enabled": ["card","email","phone","dob","address"]}` (`enabled` optional = all).

Response
```json
{
  "parts": [
    {"kind": "text", "text": "user="},
    {"kind": "pii", "rule": "email", "original": "somchai.d@company.com",
     "masked": "s*******d@company.com", "match": "somchai.d@company.com",
     "groups": {"first": "s", "middle": "omchai.", "last": "d", "domain": "company.com"},
     "info": null}
  ],
  "masked": "user=s*******d@company.com",
  "stats": {"counts": {"card": 0, "email": 1, "phone": 0, "dob": 0, "address": 0},
            "total": 1, "risk": 2, "level": "ต่ำ", "level_code": "low"}
}
```
`info` is an i18n key (`"luhn_ok"`, `"luhn_fail"`) or `null`.

## `POST /api/upload`

`multipart/form-data` with field `file` (max 5 MB). Decoded with `utf-8`, `utf-8-sig`, `cp874`, `tis-620`
in that order. `200 {"text": "…", "name": "bank.log"}` · `400 {"error": "…"}`.

## `GET /api/generate?n=25`

`n` clamped to 5..200. `200 {"text": "…"}` — `n` lines of fake log.

## `GET /api/rules`

```json
[{"key": "card", "label": "เลขบัตรเครดิต", "label_en": "Credit card number", "color": "#ef4444",
  "weight": 5, "pattern": "…raw pattern…", "flags": ["VERBOSE"], "target": 0,
  "explain": ["… — …"], "explain_en": ["… — …"],
  "example": "1234-5678-9012-3456", "example_masked": "XXXX-XXXX-XXXX-3456",
  "groups": ["g1", "sep", "g2", "g3", "last4"],
  "tokens": [["look", "(?<!"], ["cls", "[\\d-]"], ["paren", ")"], …]}]
```

## `GET /api/tests`

```json
[{"category": "card", "name_th": "ตัวอย่างโจทย์", "name_en": "Assignment example", "negative": false,
  "input": "1234-5678-9012-3456", "expected": "XXXX-XXXX-XXXX-3456",
  "actual": "XXXX-XXXX-XXXX-3456", "passed": true}]
```

## `GET /api/health`

`{"ok": true, "rules": ["card", "email", "phone", "dob", "address"]}`
