"""
Step 6 — Complex-Scenario & Exception Flagging (consolidation layer).

intake.py already produces Tier 0/1/2 ValidationIssue objects at load
time (missing fields, domain screening, related-party cross-check,
blank expanded paragraphs, near-duplicate names). This module's job —
NOT YET IMPLEMENTED — is to consolidate those with the exceptions that
can only be known AFTER tracking/reconciliation have run:
  - balance variance beyond tolerance (reconciliation.py)
  - legal response type = Limited / No Comment / silent-on-a-matter
  - intercompany variance beyond tolerance (reconciliation.py)
  - non-original response indicators (manual team input, not automatable)

Rule carried over from the spec: every exception in the final schedule
must carry its tier, its originating standard/paragraph reference where
one applies, and must be phrased as a variance requiring investigation —
never as a conclusion ("likely an error", "misstatement") that only the
engagement team is positioned to reach.
"""

from __future__ import annotations

from dataclasses import dataclass

from .intake import ValidationIssue


@dataclass
class ConsolidatedException(ValidationIssue):
    source_step: str = "intake"  # "intake" | "tracking" | "reconciliation"


def consolidate(intake_issues: list[ValidationIssue], *other_issue_lists: list[ValidationIssue]) -> list[ConsolidatedException]:
    raise NotImplementedError(
        "Merge intake_issues (already tiered) with issues raised during tracking.py "
        "and reconciliation.py once those are implemented. Preserve tier and add "
        "source_step for traceability in the final workpaper's Exception Schedule tab."
    )
