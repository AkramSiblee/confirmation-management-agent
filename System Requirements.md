# System Requirements

What a brand-new machine needs installed and configured before a new client
can run this agent end-to-end — from Step 1 (intake) through drafting,
tracking, chasing, and reconciliation. Grouped by "must have before you can
run anything" vs. "needed before specific later steps."

## 1. Core requirements (needed on day one)

| Requirement | Version | Why |
|---|---|---|
| **Python** | 3.11 or later | `pyproject.toml` pins `requires-python = ">=3.11"`. Install from [python.org](https://www.python.org/downloads/) (check "Add to PATH" on Windows) or the Microsoft Store. |
| **pip** | Bundled with Python 3.11+ | Installs the project and its dependencies. |
| **Git** | Any recent version | Version control for the codebase — this repo is the audit trail for code decisions (see `CLAUDE.md`). Install from [git-scm.com](https://git-scm.com/downloads). |
| **A code editor** | VS Code recommended | The repo ships `.vscode/settings.json` and `launch.json` (interpreter path, pytest integration, debug configs). Any editor works; VS Code is pre-wired. |
| **Claude Code CLI** | Latest | This agent is built and operated through Claude Code sessions (see `CLAUDE.md`, `.claude/skills/`). Requires **Node.js 18+** as a prerequisite for the Claude Code CLI itself. Requires a Claude subscription (Pro/Max) or an Anthropic API key. |
| **Disk space** | ~500 MB | Python packages (pandas, openpyxl, google-api client libs) plus virtual environment. Generated workpapers (`outputs/`) are gitignored and stay local. |
| **Internet access** | Required | To install Python packages from PyPI, clone/pull from Git remotes, and (later) reach Google's OAuth/Gmail/Drive APIs. |

### Python package dependencies (installed automatically)

Installed via `pip install -e ".[dev]"` — no manual installation needed, listed here for reference:

- `pandas>=2.0.0`, `openpyxl>=3.1.0` — reading/writing the Excel input/output workbooks
- `python-dateutil>=2.9.0` — chase-cadence date math
- `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib` — Gmail draft creation + Drive
- `pytest>=8.0.0` (dev only) — test suite

## 2. Initial setup sequence

```bash
git clone <repo-url>              # or copy the folder if not yet a git remote
cd confirmation-management-agent
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env              # fill in values — see Section 4
```

Then verify the install against the sample engagement:

```bash
confirmation-agent --input sample_data/confirmation-management-input-package.xlsx
pytest -v
```

Expect the intake step to print 1 Tier 0, 5 Tier 1, and 6 Tier 2 findings
against the sample workbook (see `README.md`). If that matches, the core
toolchain is working correctly.

**Windows note:** `.vscode/settings.json` points the Python interpreter at
`.venv/bin/python` (Unix-style). On Windows the venv's interpreter actually
lives at `.venv\Scripts\python.exe` — if VS Code doesn't auto-detect it,
select the interpreter manually (`Ctrl+Shift+P` → *Python: Select
Interpreter*).

## 3. Required before implementing/using Gmail & Drive integration

Needed before `dispatch.py`/`tracking.py` can create real drafts or file
workpapers to Drive — not required just to run Step 1 (intake) locally.

1. A **Google Cloud project** (client or firm IT typically owns this).
2. Enable the **Gmail API** and **Drive API** on that project.
3. Create **OAuth 2.0 Desktop-app credentials**; download the client secret
   JSON.
4. Point `GMAIL_CREDENTIALS_PATH` in `.env` at that file.
5. Request scopes must be **`gmail.compose`** (never `gmail.send`) and
   **`drive.file`** (never full Drive access) — this is enforced by design,
   not just configuration; see `integrations/google/gmail_client.py` and
   `CLAUDE.md` Rule 1 (draft-only, no send path exists in the code).
6. Set `AUDIT_TEAM_MAILBOX` in `.env` to an **audit-team-controlled**
   mailbox — never a client-provided address (control requirement under
   ISA 505/AU-C 505, see `docs/workflow-skill.md` Section 2).
7. First run will open a browser consent screen to authorize that mailbox;
   the resulting token is cached at `GMAIL_TOKEN_PATH` (gitignored).

## 4. `.env` values to fill in (copy from `.env.example`)

| Variable | Required for | Notes |
|---|---|---|
| `GMAIL_CREDENTIALS_PATH` | Gmail/Drive integration | Path to OAuth client secret JSON (Section 3) |
| `GMAIL_TOKEN_PATH` | Gmail/Drive integration | Auto-created on first OAuth consent; keep gitignored |
| `DRIVE_ROOT_FOLDER_ID` | Drive integration | Folder the agent files generated workpapers/drafts into |
| `AUDIT_TEAM_MAILBOX` | Gmail integration | Must be firm-controlled, not client-controlled |
| `DEFAULT_INPUT_WORKBOOK` | Optional | Defaults to the sample workbook; override with `--input` per engagement |

Never commit `.env`, credential JSONs, or tokens — `.gitignore` already
excludes `.env`, `*credentials*.json`, and `*token.json`.

## 5. Needed later (once `workpaper.py` produces formula-bearing output)

- **LibreOffice** (headless mode) — recommended for recalculating generated
  workbooks before treating them as final. Cached-but-unrecalculated Excel
  formulas read back as blank in most downstream tools, so this is a
  verification step, not optional. Install from
  [libreoffice.org](https://www.libreoffice.org/download/download/); the
  `soffice` binary must be on PATH for headless recalculation commands to
  work.
- **Microsoft Excel or another spreadsheet app** — for a human reviewer to
  open real client input workbooks and generated output workpapers. Not a
  code dependency, but the engagement team will need one.

## 6. What is *not* required

- No database — all state is read from/written to Excel workbooks.
- No cloud hosting/server — this runs as a local CLI tool per engagement.
- No e-confirmation platform account yet — `integrations/econfirmation/` is
  a placeholder with no provider wired up (see `README.md` build-state
  table).
- No admin rights beyond installing Python/Git/VS Code/Claude Code
  normally — the agent itself needs no elevated permissions.

## 7. Per-client / per-engagement setup (not machine setup, but often confused with it)

- A real input workbook matching the schema in `docs/io-spec.md` Section 1
  (column headers, tab names, header-row offsets) — the sample workbook is
  for testing only.
- Confirmation that the mailbox in `AUDIT_TEAM_MAILBOX` is under the audit
  firm's control for this engagement, not the client's.
- Jurisdiction/template-standard values populated correctly in the input
  workbook so `templates.py` can select the right letter template per
  counterparty (`CLAUDE.md` Rule 7).
