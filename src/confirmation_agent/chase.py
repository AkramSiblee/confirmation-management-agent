"""
Step 5 — Chase Cadence.

Drafts chase emails for eligible non-responders. NOT YET IMPLEMENTED.

CRITICAL RULE (docs/workflow-skill.md Section 5 and Section 7 Quality
Standards): AR Negative confirmations are NEVER chased. Per ISA
505.20/AU-C 505, a non-reply to a negative confirmation is the expected
outcome, not evidence of anything, and is not queued for follow-up. If
you are extending this module, the very first thing any cadence
function should do is filter out `confirmation_type == "ar"` rows where
`row["Confirmation Type"] == schemas.AR_NEGATIVE_VALUE` — before any
days-outstanding math runs at all.
"""

from __future__ import annotations

from datetime import date

from . import rules, schemas


def is_chase_eligible(tracker_row, population_row, confirmation_type: str) -> bool:
    if confirmation_type == "ar" and population_row.get("Confirmation Type") == schemas.AR_NEGATIVE_VALUE:
        return False
    return tracker_row.status == "Outstanding"


def due_chase_tier(days_outstanding: int, confirmation_type: str, cadence: rules.Cadence = rules.DEFAULT_CADENCE) -> str | None:
    if confirmation_type == "legal":
        if days_outstanding >= cadence.legal_escalate:
            return "escalate"
        if days_outstanding >= cadence.legal_first:
            return "first"
        return None
    if days_outstanding >= cadence.bank_ar_escalate:
        return "escalate"
    if days_outstanding >= cadence.bank_ar_second:
        return "second"
    if days_outstanding >= cadence.bank_ar_first:
        return "first"
    return None


def draft_chase_email(tracker_row, population_row, tier: str):
    raise NotImplementedError(
        "Draft via templates.py's chase-letter variant, then dispatch.create_draft_and_log "
        "with confirmation_type carried through. Increment tracker_row.chase_count."
    )
