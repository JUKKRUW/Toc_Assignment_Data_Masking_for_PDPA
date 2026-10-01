# PDPA Shield

Regex-based data masking for banking logs — Theory of Computation (ToC) assignment.

A web application that finds personal data in a bank's log files and masks it according to PDPA rules,
using **only Python's `re` module** for detection and masking.

| Data | Input | Output |
|---|---|---|
| Credit card | `1234-5678-9012-3456` | `XXXX-XXXX-XXXX-3456` |
| Email | `somchai.d@company.com` | `s*******d@company.com` |
| Phone | `093-245-7894` | `XXX-XXX-7894` |
| Date of birth | `DOB:25/12/2549` | `DOB:XX/XX/25XX` |
| Address | `Address: 689 ซอย… ถนน… แขวง… เขต… กรุงเทพฯ` | `Address: XXX ซอย… ถนน… แขวง… เขต… กรุงเทพฯ` |

## Status

This is the **team skeleton**. Every module has an owner, a spec in its docstring, and acceptance tests.
Unimplemented stubs raise `NotImplementedError`, which the test suite reports as **XFAIL** — so CI stays
green while work is in progress, and a test turns into a real pass/fail the moment its stub is filled in.

```
pytest -q        # 1 passed, 93 xfailed   <- today
pytest -q        # 94 passed              <- definition of done
```

A complete working version lives on the **`reference`** branch (see [docs/TEAM.md](docs/TEAM.md#reference-branch)).

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest -q                                              # run the acceptance tests
ruff check .                                           # lint
flask --app pdpa_shield.app run --debug                # http://127.0.0.1:5000
```

## Repository layout

```
pdpa_shield/
  engine/types.py      shared contracts (Rule, Part, Stats)            M01
  cases.py             canonical acceptance cases (pytest + UI)        M01
  rules/card.py        credit card rule                                M02
  rules/email.py       email rule                                      M03
  rules/phone.py       phone rule                                      M04
  rules/dob.py         date-of-birth rule                              M05
  rules/address.py     address rule                                    M06
  engine/registry.py   rule priority order                             M07
  engine/scanner.py    scan + overlap resolution + mask_text           M07
  engine/risk.py       PDPA risk score                                 M07
  engine/highlight.py  regex syntax highlighter (written with re)      M07
  app.py               Flask API                                       M08
  loggen.py            fake banking-log generator                      M08
web/
  templates/index.html app shell                                       M09
  static/css/tokens.css design tokens (shared)                         M09 + M10
  static/js/api.js     HTTP client                                     M08
  static/js/{app,i18n,icons,mask}.js   shell, i18n, icons, page 01     M09
  static/js/{rules,tests,dfa}.js       pages 02, 03, 04                M10
tests/                 acceptance tests (one file per owner)
docs/                  TEAM, ARCHITECTURE, API, DESIGN
scripts/               GitHub bootstrap (repo, labels, milestones, issues)
```

## Live website (GitHub Pages)

The **Deploy website** workflow (`.github/workflows/pages.yml`) publishes a static copy to
`https://<owner>.github.io/<repo>/`. GitHub Pages cannot run Flask, so the static build loads
**Pyodide** (CPython compiled to WebAssembly) and runs the same `pdpa_shield` package in the browser:
masking is still done by Python's `re`, and uploaded logs never leave the visitor's machine.

- Today it publishes the `reference` branch. When the team is done, run the workflow with
  `source = main` (or change the default in `pages.yml`).
- One-time setup: **Settings → Pages → Source: GitHub Actions** (the bootstrap script tries to do this).
- Free accounts need a **public** repo for Pages.
- Preview locally: `python scripts/build_site.py && python -m http.server -d _site 8000` (on `reference`).

## Documentation

- [docs/TEAM.md](docs/TEAM.md) — roles, tasks and timeline for the 10 members
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — modules, data flow, the DFA
- [docs/API.md](docs/API.md) — HTTP contract between backend and frontend
- [docs/DESIGN.md](docs/DESIGN.md) — design system (Liquid Glass, spacing, motion, i18n)
- [CONTRIBUTING.md](CONTRIBUTING.md) — branches, commits, pull requests
