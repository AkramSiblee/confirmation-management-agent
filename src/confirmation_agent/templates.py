"""
Step 2 — Template Selection & Drafting.

Maps each validated population record to the correct letter template by
type, sub-type, and jurisdiction (docs/workflow-skill.md Step 2;
io-spec.md 1.2-1.4). NOT YET IMPLEMENTED — this module is the next build
increment once intake.py's output (an IntakeResult) is treated as final
for a run.

Design constraints carried over from the spec (do not relax these when
implementing):
  - One generic bank letter is a compliance gap in a multi-jurisdiction
    group audit — US/UK/Canada each get their own template.
  - Legal letters must include the unbilled/unpaid fee request and the
    "substantive attention" scope-limit framing.
  - A record with an unresolved Tier 0 or Tier 1 issue (see intake.py)
    must NOT be drafted until the issue is cleared or explicitly
    overridden by the team — drafting should refuse, not warn-and-proceed.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Jurisdiction(str, Enum):
    US_AICPA_ABA_BAI = "US-AICPA/ABA/BAI"
    UK_ICAEW = "UK-ICAEW"
    CA_CPACANADA = "CA-CPACanada"


TEMPLATE_PATHS = {
    # Populate with real template file paths/strings once drafted with
    # the engagement team. Kept as a lookup table so adding a fourth
    # jurisdiction is a data change, not a code change.
    (Jurisdiction.US_AICPA_ABA_BAI, "Standard"): "templates/bank/us_standard.txt",
    (Jurisdiction.US_AICPA_ABA_BAI, "Expanded"): "templates/bank/us_expanded.txt",
    (Jurisdiction.UK_ICAEW, "Standard"): "templates/bank/uk_standard.txt",
    (Jurisdiction.UK_ICAEW, "Expanded"): "templates/bank/uk_expanded.txt",
    (Jurisdiction.CA_CPACANADA, "Standard"): "templates/bank/ca_standard.txt",
    (Jurisdiction.CA_CPACANADA, "Expanded"): "templates/bank/ca_expanded.txt",
}


@dataclass
class DraftedLetter:
    record_reference: str
    template_used: str
    body: str
    recipient_email: str


def draft_bank_letter(row) -> DraftedLetter:
    raise NotImplementedError(
        "Implement using TEMPLATE_PATHS keyed on (Jurisdiction, Confirmation Form Type). "
        "Include every Non-Standard Paragraph Requested verbatim (io-spec.md 1.2)."
    )


def draft_ar_letter(row) -> DraftedLetter:
    raise NotImplementedError(
        "Positive-Standard pre-prints the balance; Positive-Blank must NOT show the "
        "balance (the counterparty fills it in); Negative uses the negative-form wording "
        "and must clearly state a reply is only needed if the recipient disagrees."
    )


def draft_legal_letter(row, *, is_bring_down: bool = False) -> DraftedLetter:
    raise NotImplementedError(
        "Include the unbilled/unpaid fee request and the substantive-attention framing "
        "(io-spec.md 1.4). If is_bring_down, use the shorter update-letter template and "
        "reference the original letter's date."
    )
