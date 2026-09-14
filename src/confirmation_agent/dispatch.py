"""
Step 3 — Dispatch Logging.

Creates a Gmail DRAFT (never sends) for each letter from templates.py,
saves the letter body to Drive, and logs the dispatch (sent/created
date, method, jurisdiction/template used, due date per the cadence
policy, initial tracker status) — docs/workflow-skill.md Step 3.

Hard rule carried over from the spec (docs/workflow-skill.md Section 7,
Quality standards): no code path in this module may call Gmail's send
API. If you find yourself importing anything other than create_draft
from integrations/google/gmail_client.py, stop — that belongs in a
human-triggered step outside this agent.

Initial tracker status per workflow-skill.md Step 3:
  - Positive (bank/AR) and legal items open as "Outstanding".
  - AR Negative items open on the distinct non-chased track,
    "Delivered — No Reply (Expected)" — never "Outstanding" (CLAUDE.md
    Rule 2; chase.py must also filter these out independently, this
    status label is not the only gate).
  - Intercompany items open as "Pending Component Response" — this is
    an internal ISA 600-adjacent request, not governed by the Bank/AR/
    Legal chase cadence, so it gets no due_date here.

A note on `sent_date`: this agent never calls send — a human sends the
Gmail draft later, at their own pace. `sent_date` here really means
"the date this dispatch was logged / the draft was created," used only
to seed a planning due_date. Once tracking.py exists, it should let the
team overwrite this with the actual date they hit send in Gmail, if
different.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, timedelta

from . import rules
from .integrations.google import drive_client, gmail_client
from .templates import DraftedLetter, DraftingBatch

# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class DispatchRecord:
    record_reference: str
    confirmation_type: str  # "bank" | "ar" | "legal" | "legal-bring-down" | "intercompany"
    sent_date: date
    method: str  # "email" | "mail" | "e-confirmation-platform"
    jurisdiction_or_template: str
    status: str
    due_date: date | None  # None where the record isn't on a chase-cadence track (see module docstring)
    recipient_email: str
    gmail_draft_id: str | None = None
    drive_file_id: str | None = None


class DispatchError(RuntimeError):
    """Raised for a single record's dispatch failure (e.g. no recipient
    email on file). Collected in DispatchBatch.errors rather than
    aborting the whole run — one bad record must not block the rest."""


@dataclass
class DispatchBatch:
    dispatched: list[DispatchRecord] = field(default_factory=list)
    errors: list[tuple[str, str]] = field(default_factory=list)  # (record_reference, reason)
    # Cadence-parsing fallbacks and similar — feeds the Step 8 Changelog
    # (workflow-skill.md Section 6, "Explicit over silent": every
    # assumption logged, never silently defaulted).
    assumptions: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Business-day arithmetic
# ---------------------------------------------------------------------------


def add_business_days(start: date, business_days: int) -> date:
    """Add N business days (Mon-Fri). No jurisdiction-specific holiday
    calendar yet — a US/UK/Canada engagement spans different holiday
    schedules, so treat a due_date near a known holiday as approximate
    until one is added."""
    current = start
    step = 1 if business_days >= 0 else -1
    remaining = abs(business_days)
    while remaining > 0:
        current += timedelta(days=step)
        if current.weekday() < 5:  # Monday=0 ... Sunday=6
            remaining -= 1
    return current


# ---------------------------------------------------------------------------
# Cadence resolution — Engagement Setup's cadence fields are free text
# (e.g. "1st: 10 / 2nd: 20 / Escalate: 30 — positive confirmations only,
# not applied to negative"), not a structured number. Parse the first
# chase interval out of it; if that fails, fall back to rules.py's
# default and record it as an assumption rather than silently guessing.
# ---------------------------------------------------------------------------

_FIRST_CADENCE_RE = re.compile(r"1st:\s*(\d+)", re.IGNORECASE)


def _resolve_first_cadence(engagement: dict, field_name: str, default_days: int) -> tuple[int, bool]:
    raw = str(engagement.get(field_name, ""))
    match = _FIRST_CADENCE_RE.search(raw)
    if match:
        return int(match.group(1)), False
    return default_days, True


# ---------------------------------------------------------------------------
# Per-record dispatch
# ---------------------------------------------------------------------------


def _initial_status(letter: DraftedLetter) -> str:
    if letter.confirmation_type == "ar" and letter.is_negative_ar:
        return "Delivered — No Reply (Expected)"
    if letter.confirmation_type == "intercompany":
        return "Pending Component Response"
    return "Outstanding"


def _subject_for(letter: DraftedLetter) -> str:
    kind = {
        "bank": "Bank Confirmation Request",
        "ar": "Accounts Receivable Confirmation Request",
        "legal": "Letter of Audit Inquiry",
        "legal-bring-down": "Bring-Down Letter of Audit Inquiry",
        "intercompany": "Intercompany Balance Agreement — Data Request",
    }.get(letter.confirmation_type, "Audit Confirmation Request")
    return f"{kind} — {letter.record_reference}"


def _safe_filename(reference: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", reference).strip("_")[:150] or "record"


def create_draft_and_log(
    letter: DraftedLetter,
    *,
    cadence_days: int | None,
    drive_folder_id: str,
    sender: str,
    dispatch_date: date | None = None,
    dry_run: bool = False,
) -> DispatchRecord:
    """Save `letter.body` to Drive, create a Gmail draft addressed to
    `letter.recipient_email` from `sender` (the audit-team-controlled
    mailbox), and return a DispatchRecord for the tracker.

    dry_run=True skips both real API calls (useful before Google OAuth
    is configured, or to preview what a run would do) but still enforces
    the same validation — e.g. a missing recipient email still raises,
    so a dry run's blocked-record list matches what a live run would
    produce.
    """
    if not letter.recipient_email:
        raise DispatchError(
            f"No recipient email on file for '{letter.record_reference}' — cannot create a Gmail draft. "
            "For intercompany requests this is expected (io-spec.md's Intercompany tab has no contact-"
            "email column); supply the internal contact directly before dispatch."
        )

    dispatch_date = dispatch_date or date.today()
    subject = _subject_for(letter)
    status = _initial_status(letter)

    due_date = None
    if status == "Outstanding" and cadence_days is not None:
        due_date = add_business_days(dispatch_date, cadence_days)

    if dry_run:
        drive_file_id = f"dry-run:drive:{_safe_filename(letter.record_reference)}"
        gmail_draft_id = f"dry-run:gmail:{_safe_filename(letter.record_reference)}"
    else:
        drive_file_id = drive_client.upload_text_file(
            filename=f"{_safe_filename(letter.record_reference)}.txt",
            content=letter.body,
            folder_id=drive_folder_id,
        )
        gmail_draft_id = gmail_client.create_draft(
            to=letter.recipient_email,
            subject=subject,
            body=letter.body,
            sender=sender,
        )

    return DispatchRecord(
        record_reference=letter.record_reference,
        confirmation_type=letter.confirmation_type,
        sent_date=dispatch_date,
        method="email",
        jurisdiction_or_template=letter.template_used,
        status=status,
        due_date=due_date,
        recipient_email=letter.recipient_email,
        gmail_draft_id=gmail_draft_id,
        drive_file_id=drive_file_id,
    )


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def dispatch_all(
    batch: DraftingBatch,
    engagement: dict,
    *,
    drive_folder_id: str,
    sender: str,
    dispatch_date: date | None = None,
    dry_run: bool = False,
) -> DispatchBatch:
    """Dispatch every letter templates.py drafted. A single record's
    failure (missing recipient, API error) is collected in .errors
    rather than aborting the run."""
    result = DispatchBatch()

    bank_ar_cadence, bank_ar_assumed = _resolve_first_cadence(
        engagement, "Chase Cadence — Bank/AR (business days)", rules.DEFAULT_CADENCE.bank_ar_first
    )
    legal_cadence, legal_assumed = _resolve_first_cadence(
        engagement, "Chase Cadence — Legal (business days)", rules.DEFAULT_CADENCE.legal_first
    )
    if bank_ar_assumed:
        result.assumptions.append(
            f"Bank/AR first-chase cadence defaulted to {bank_ar_cadence} business days — could not parse "
            "a number from Engagement Setup's cadence field; team should confirm."
        )
    if legal_assumed:
        result.assumptions.append(
            f"Legal first-chase cadence defaulted to {legal_cadence} business days — could not parse a "
            "number from Engagement Setup's cadence field; team should confirm."
        )

    for letter in batch.drafted:
        cadence_days = legal_cadence if letter.confirmation_type in ("legal", "legal-bring-down") else bank_ar_cadence
        try:
            record = create_draft_and_log(
                letter,
                cadence_days=cadence_days,
                drive_folder_id=drive_folder_id,
                sender=sender,
                dispatch_date=dispatch_date,
                dry_run=dry_run,
            )
            result.dispatched.append(record)
        except DispatchError as exc:
            result.errors.append((letter.record_reference, str(exc)))

    return result


def summarize_dispatch(batch: DispatchBatch, *, dry_run: bool) -> str:
    lines = ["Confirmation Management Agent — Dispatch Summary (Step 3)", "=" * 58]
    if dry_run:
        lines.append(
            "DRY RUN — no real Gmail draft or Drive file was created. Configure "
            "GMAIL_CREDENTIALS_PATH / AUDIT_TEAM_MAILBOX / DRIVE_ROOT_FOLDER_ID in .env "
            "(see README.md 'Google Workspace setup') and pass --live to dispatch for real."
        )
        lines.append("")

    lines.append(f"Dispatched: {len(batch.dispatched)}")
    by_status: dict[str, int] = {}
    for d in batch.dispatched:
        by_status[d.status] = by_status.get(d.status, 0) + 1
    for status, count in sorted(by_status.items()):
        lines.append(f"  {status}: {count}")

    if batch.assumptions:
        lines.append("")
        lines.append("Assumptions (carry forward to the Step 8 Changelog):")
        for a in batch.assumptions:
            lines.append(f"  - {a}")

    if batch.errors:
        lines.append("")
        lines.append(f"Errors ({len(batch.errors)}):")
        for ref, reason in batch.errors:
            lines.append(f"  - {ref}: {reason}")

    return "\n".join(lines)
