# Confirmation Management Agent

Drafts, tracks, chases, and reconciles bank, AR, and legal external audit
confirmations — plus intercompany balance agreement — for multi-jurisdiction
group audits. Built for Big 4-caliber engagements; sold as pure administrative
relief: no audit judgment is automated, only the clerical load around it.

Full specification: [`docs/workflow-skill.md`](docs/workflow-skill.md) (methodology,
standards basis, RACI, execution steps) and [`docs/io-spec.md`](docs/io-spec.md)
(column-level input schemas, flagging framework, output tab structure). The
`.claude/skills/` copy is a slim router pointing back at these two — see
"Repository conventions" below for why.

## Current build state

| Step | Module | Status |
|---|---|---|
| 1. Intake & Validation | `src/confirmation_agent/intake.py` | **Implemented & tested** |
| 2. Template Selection & Drafting | `templates.py` | Scaffolded — next increment |
| 3. Dispatch Logging | `dispatch.py` | Scaffolded |
| 4. Response Tracking & Matching | `tracking.py` | Scaffolded |
| 5. Chase Cadence | `chase.py` | Scaffolded |
| 6. Exception Schedule Consolidation | `exception_schedule.py` | Scaffolded |
| 7. Reconciliation (GL & Intercompany) | `reconciliation.py` | Scaffolded |
| 8. Workpaper Generation | `workpaper.py` | Scaffolded |
| Gmail/Drive integration | `integrations/google/` | Scaffolded — draft-only by design |
| E-confirmation platform integration | `integrations/econfirmation/` | Placeholder — no provider wired up yet |

Every scaffolded module has a full docstring citing the exact io-spec/workflow-skill
section it must satisfy, plus `NotImplementedError` bodies naming the concrete next
step — start a Claude Code session in this folder and point it at one module at a
time, in order, rather than asking for everything at once. Recommended order:
`templates.py` → `dispatch.py` → `tracking.py` → `chase.py` → `reconciliation.py`
→ `exception_schedule.py` → `workpaper.py` (see `CLAUDE.md`).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"          # editable install + pytest
cp .env.example .env             # fill in Google OAuth + engagement details
```

The editable install registers a `confirmation-agent` console script and makes
`confirmation_agent` importable from anywhere in the repo — no `PYTHONPATH`
juggling needed, in the terminal or in VS Code.

## Running Step 1 against the sample engagement

```bash
confirmation-agent --input sample_data/confirmation-management-input-package.xlsx
# equivalent: python -m confirmation_agent.main --input ...
```

This loads `sample_data/confirmation-management-input-package.xlsx` — a
deliberately imperfect Meridian Supply Group (fictional) group-audit
package spanning US/UK/Canada entities — and prints every Tier 0/1/2 issue
the agent found. Expected output: 1 Tier 0 (a look-alike bank domain),
5 Tier 1 (missing contact emails), 6 Tier 2 (understated related-party
flags, a blank non-standard-paragraph selection, two near-duplicate
counterparty names). See `tests/test_intake.py` for the full assertion set.

## Tests

```bash
pytest -v
```

No `sys.path` hacks in the test files — `pyproject.toml`'s
`[tool.pytest.ini_options] pythonpath = ["src"]` handles it, whether or not
you've done the editable install.

## VS Code

Opening the repo root in VS Code picks up `.vscode/settings.json` (interpreter
path, pytest integration, `src` added to the analysis path) and
`.vscode/launch.json` (two debug configs: run Step 1 against the sample
workbook, or debug whichever test file is open). Select the `.venv`
interpreter created above if VS Code doesn't pick it up automatically.

## Google Workspace setup (required before implementing dispatch.py / tracking.py)

1. Create a Google Cloud project, enable the **Gmail API** and **Drive API**.
2. Create OAuth 2.0 Desktop-app credentials; download the client secret JSON.
3. Set `GMAIL_CREDENTIALS_PATH` in `.env` to that file's path.
4. Request scopes are **compose-only for Gmail** (`gmail.compose`, never
   `gmail.send`) and **file-scoped for Drive** (`drive.file`, never full
   Drive access) — see `integrations/google/gmail_client.py` and
   `drive_client.py` for why, and do not widen these scopes.
5. Set `AUDIT_TEAM_MAILBOX` to the mailbox drafts should be created from —
   never a client-controlled address (this is a control requirement under
   ISA 505/AU-C 505, not a style preference — see `docs/workflow-skill.md`
   Section 2).

## Repository conventions

See [`CLAUDE.md`](CLAUDE.md) — the persistent knowledge layer for Claude Code
sessions working in this repo. Read it before making changes; update it
when you learn something a future session needs to know.

Two things worth knowing up front:
- **`config.py` vs `rules.py`**: `config.py` only answers "where/how is the
  workbook laid out" (paths, sheet names, header-row offsets). `rules.py`
  holds every audit-judgment-adjacent default (tolerances, chase cadence,
  flag-tier labels) in one place, since those are the values a reviewer
  most needs to be able to find and sanity-check at a glance.
- **`docs/` is the single source of truth for the spec.** The
  `.claude/skills/.../SKILL.md` Claude Code loads automatically is a slim
  router (trigger phrases + a quick-reference list + links back to
  `docs/`) rather than a second full copy — keeps the two from drifting
  apart and keeps Claude Code's per-trigger context smaller.

## Folder structure

```
confirmation-management-agent/
├── pyproject.toml                   # packaging, console script, pytest config
├── CLAUDE.md                        # persistent knowledge layer — read first
├── README.md                        # this file
├── .env.example
├── .gitignore
├── .vscode/
│   ├── settings.json                # interpreter, pytest integration, src path
│   └── launch.json                  # debug configs (run sample data / current test)
├── .claude/skills/confirmation-management-agent/
│   └── SKILL.md                     # slim trigger/router file -> points to docs/
├── docs/
│   ├── workflow-skill.md            # methodology, standards, RACI, steps (canonical)
│   └── io-spec.md                   # input schemas, flagging framework, output spec
├── sample_data/
│   └── confirmation-management-input-package.xlsx   # test engagement, intentionally imperfect
├── src/confirmation_agent/
│   ├── __init__.py                  # version + convenience exports (load_all, etc.)
│   ├── config.py                    # I/O layout: paths, sheet names, header offsets
│   ├── rules.py                     # business defaults: tolerances, cadence, flag tiers
│   ├── schemas.py                   # column-level schema constants (mirrors io-spec.md)
│   ├── matching.py                  # domain look-alike + near-duplicate name proposals
│   ├── intake.py                    # Step 1 — IMPLEMENTED
│   ├── templates.py                 # Step 2 — scaffold
│   ├── dispatch.py                  # Step 3 — scaffold
│   ├── tracking.py                  # Step 4 — scaffold
│   ├── chase.py                     # Step 5 — scaffold
│   ├── exception_schedule.py        # Step 6 — scaffold
│   ├── reconciliation.py            # Step 7 — scaffold
│   ├── workpaper.py                 # Step 8 — scaffold
│   ├── integrations/
│   │   ├── google/
│   │   │   ├── gmail_client.py      # draft-only, never send
│   │   │   └── drive_client.py
│   │   └── econfirmation/           # placeholder — no platform wired up yet
│   └── main.py                      # CLI entrypoint (also the `confirmation-agent` script)
├── tests/
│   └── test_intake.py               # 8 passing tests against the sample workbook
└── outputs/                         # generated workpapers land here (gitignored)
```
