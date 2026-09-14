"""
Step 3 — Dispatch Logging.

Creates a Gmail DRAFT (never sends) for each letter from templates.py,
from the audit-team-controlled mailbox configured in .env, and logs the
dispatch in the tracker (sent date, method, jurisdiction/template used,
due date per the cadence policy). NOT YET IMPLEMENTED.

Hard rule carried over from the spec (docs/workflow-skill.md Section 7,
Quality standards): no code path in this module may call Gmail's send
API. If you find yourself importing anything other than a "create draft"
call from integrations/google/gmail_client.py, stop — that belongs in a
human-triggered step outside this agent.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class DispatchRecord:
    record_reference: str
    confirmation_type: str  # "bank" | "ar" | "legal"
    sent_date: date
    method: str  # "email" | "mail" | "e-confirmation-platform"
    jurisdiction_or_template: str
    due_date: date
    gmail_draft_id: str | None = None
    drive_file_id: str | None = None


def create_draft_and_log(letter, *, confirmation_type: str, cadence_days: int) -> DispatchRecord:
    raise NotImplementedError(
        "1) Save `letter.body` to Drive (integrations/google/drive_client.py). "
        "2) Create a Gmail draft (integrations/google/gmail_client.py: create_draft — "
        "NEVER send_message) addressed to letter.recipient_email, from the "
        "audit-team mailbox in config/.env. "
        "3) Return a DispatchRecord with both artifact ids for the tracker."
    )
