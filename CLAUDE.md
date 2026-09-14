# CLAUDE.md — Confirmation Management Agent

Persistent knowledge layer. Read this before making changes. Update it when
you learn something a future session needs to know — this file is the audit
trail for *decisions*, not a changelog for every commit (Git handles that).

## What this agent is, in one paragraph

Administrative relief for the external-confirmation process on a Big
4-caliber, multi-jurisdiction group audit: drafts (never sends) bank/AR/legal
confirmations and intercompany balance-agreement requests, tracks responses,
chases non-responders on the correct cadence, screens for confirmation fraud
indicators, and reconciles confirmed balances to GL. It never selects the
sample, sets confirmation strategy, judges evidence sufficiency, or resolves
an exception — those stay with the engagement team. Full spec: `docs/`.

## Non-negotiable design rules (do not relax these while building)

1. **Draft-only.** No code path anywhere in this repo calls Gmail's
   `send_message`/`send`. `integrations/google/gmail_client.py` only exposes
   `create_draft`. If a task seems to require sending, the task is wrong —
   flag it back to the user rather than adding a send path.
2. **Negative AR confirmations are never chased.** A non-reply is the
   expected outcome (ISA 505.20/AU-C 505), not an "Outstanding" item. `chase.py`
   filters these out before any days-outstanding math runs. If you add a new
   entry point into the chase logic, filter there too — don't assume the
   existing filter is the only door in.
3. **Self-reported "Related Party?" flags are never trusted alone.** Always
   cross-reference the independent Related Party List tab. `intake.py`
   already does this for Bank and AR; extend the same pattern for any new
   population type rather than reading the self-reported column directly.
4. **Every translated (FX) figure must cite its rate source.** Pull it from
   `IntakeResult.engagement["FX Rate Source & Convention"]`. An unsourced
   translated number is a bug, not a minor omission — it fails the pre-delivery
   checklist in `docs/io-spec.md` Section 10.
5. **A flagged exception is a variance requiring investigation, never a
   conclusion.** Don't write "error" or "misstatement" anywhere in generated
   output copy — that's the engagement team's call, not the agent's.
6. **A proposed match is never an automatic merge.** `matching.py`'s
   near-duplicate name and look-alike domain functions return proposals with
   a similarity score; nothing downstream should collapse two records into
   one without an explicit team confirmation step.
7. **Jurisdiction drives template selection — no generic template.** A US
   bank, a UK bank, and a Canadian bank in the same population get three
   different letter templates (`templates.py`'s `TEMPLATE_PATHS`), keyed by
   `Jurisdiction / Template Standard`.
8. **`config.py` vs `rules.py` stay separate.** `config.py` only answers
   "where/how is the workbook laid out" (paths, sheet names, header-row
   offsets). Any new audit-judgment-adjacent default (a tolerance, a
   cadence, a tier label) goes in `rules.py`. If you're about to add a
   constant to `config.py` and it isn't a path or a layout offset, it
   belongs in `rules.py` instead.
9. **pandas `keep_default_na=False` on every population/engagement-setup
   read.** See the comment in `intake.py` above `_READ_KWARGS` — several
   fields legitimately use the literal string `"N/A"` as data (e.g. a
   retainer-only legal matter), and pandas' default NA-string list will
   silently eat it and produce a false Tier 1 hard gate if you forget this.
   This bit us once already during the initial build; don't reintroduce it
   in a new `read_excel` call.

## Known failure modes to check whenever you touch a module

- **Tab/column name drift.** `schemas.py` must mirror `docs/io-spec.md`
  Section 1 exactly. If you change a column header in the sample workbook or
  a real engagement file, update `io-spec.md` first, then `schemas.py`, then
  re-run `tests/test_intake.py` — in that order. If a *real client's* export
  simply doesn't match `io-spec.md` (different tab names, renamed columns,
  shifted header row), do not loosen `intake.py`'s validation or make
  `schemas.py` "flexible" to cope — write a small `AdapterSpec` in
  `src/confirmation_agent/intake_adapters/` instead (copy
  `example_client.py`) and pass it via `load_all(path, adapter=...)` /
  `--adapter <name>`. It normalizes that one client's layout onto the
  canonical schema before validation runs, so `schemas.py`/`io-spec.md`
  stay the single source of truth every downstream module relies on.
- **Header-row offset.** Population tabs have `header=2` (title + subtitle +
  header at Excel row 3); Engagement Setup has `header=3, usecols="B:C"` (see
  `config.py`). A new sheet built with a different `write_table`/layout
  convention will silently misalign columns if this offset isn't matched.
- **Rollforward blind spot.** Any reconciliation logic must check
  `Rollforward Required` in Engagement Setup and use *both* GL Balance
  columns for bank items — a static single-column compare is wrong whenever
  confirmation date ≠ period-end.
- **Currency-before-translation ordering.** Reconcile local-currency figures
  first, always. A translated-only comparison risks mistaking an FX-timing
  gap for a real discrepancy (or vice versa).

## Build sequencing (recommended order for the remaining steps)

`templates.py` → `dispatch.py` → `tracking.py` → `chase.py` → `reconciliation.py`
→ `exception_schedule.py` (consolidation, so it can pull from tracking + reconciliation)
→ `workpaper.py` (needs everything upstream). Implement and test each module
against `sample_data/confirmation-management-input-package.xlsx` before moving
to the next — the sample data's planted issues (look-alike domain, understated
related-party flags, genuine reconciliation variances in the bank/AR/intercompany
tabs, blank expanded paragraph, near-duplicate names) exist specifically to
exercise each step's detection logic, not just its happy path.

## Toolchain

- Python 3.11+, `pandas` + `openpyxl` for data; `google-api-python-client` +
  `google-auth-oauthlib` for Gmail/Drive.
- Tests: `pytest`.
- Verification: LibreOffice headless recommended for `workpaper.py` output
  once formulas are introduced (recalculate before treating a workbook as
  final — cached-but-unrecalculated formulas read back as blank in most
  downstream tools).
- No secrets in the repo: `.env` is gitignored; `.env.example` documents the
  required variables without values.

## Auditability

This Git repo is the audit trail for the *codebase's* decisions (this file),
separate from the audit engagement's own workpapers (which live in the
generated `outputs/*.xlsx`, gitignored, and in the firm's Drive/DMS). Keep
that boundary clean — don't commit generated workpapers or real client data
into this repo.
