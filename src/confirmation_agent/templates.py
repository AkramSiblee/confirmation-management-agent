"""
Step 2 — Template Selection & Drafting.

Maps each validated population record to the correct letter template by
type, sub-type, and jurisdiction (docs/workflow-skill.md Step 2;
io-spec.md 1.2-1.4), and renders the letter body. Letter text bodies live
as plain-text files under templates/ (project root), keyed by
TEMPLATE_PATHS-style lookup tables below, so a firm can edit wording
without touching this module.

Design constraints carried over from the spec (do not relax these when
extending this module):
  - One generic bank letter is a compliance gap in a multi-jurisdiction
    group audit — US/UK/Canada each get their own template (CLAUDE.md
    Rule 7). An unrecognized/"Other" jurisdiction raises rather than
    falling back to a default letter.
  - Legal letters must include the unbilled/unpaid fee request and the
    "substantive attention" scope-limit framing.
  - A record with an unresolved Tier 0 or Tier 1 issue (see intake.py)
    must NOT be drafted until the issue is cleared or explicitly
    overridden by the team — drafting refuses (DraftingBlocked), it
    does not warn-and-proceed.
  - AR Positive-Blank must NEVER show the balance in the letter body —
    see templates/ar/positive_blank.txt, which has no $balance
    placeholder at all (not just a blanked-out value).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from string import Template

from . import config, rules

# ---------------------------------------------------------------------------
# Jurisdiction / template lookup tables
# ---------------------------------------------------------------------------


class Jurisdiction(str, Enum):
    US_AICPA_ABA_BAI = "US-AICPA/ABA/BAI"
    UK_ICAEW = "UK-ICAEW"
    CA_CPACANADA = "CA-CPACanada"


TEMPLATE_PATHS = {
    # Bank: (Jurisdiction, Confirmation Form Type) -> file under templates/, relative to config.TEMPLATES_DIR.
    (Jurisdiction.US_AICPA_ABA_BAI, "Standard"): "bank/us_standard.txt",
    (Jurisdiction.US_AICPA_ABA_BAI, "Expanded"): "bank/us_expanded.txt",
    (Jurisdiction.UK_ICAEW, "Standard"): "bank/uk_standard.txt",
    (Jurisdiction.UK_ICAEW, "Expanded"): "bank/uk_expanded.txt",
    (Jurisdiction.CA_CPACANADA, "Standard"): "bank/ca_standard.txt",
    (Jurisdiction.CA_CPACANADA, "Expanded"): "bank/ca_expanded.txt",
}

AR_TEMPLATE_PATHS = {
    "Positive-Standard": "ar/positive_standard.txt",
    "Positive-Blank": "ar/positive_blank.txt",
    "Negative": "ar/negative.txt",
}

LEGAL_TEMPLATE_PATHS = {
    "standard": "legal/standard.txt",
    "bring_down": "legal/bring_down.txt",
}

INTERCOMPANY_TEMPLATE_PATH = "intercompany/data_request.txt"

# Request wording for each recognized non-standard paragraph type
# (io-spec.md 1.2). An unrecognized token still renders (with a
# placeholder asking the team to supply wording) rather than being
# silently dropped from the letter.
PARAGRAPH_LIBRARY = {
    "Compensating Balance": (
        "Please state whether any compensating balance arrangements exist "
        "on the account(s) above, including the terms of any such arrangement."
    ),
    "LOC": (
        "Please confirm the terms, available amount, and amount drawn (if "
        "any) on any letter(s) of credit issued for the account holder's "
        "benefit."
    ),
    "Guarantee": (
        "Please confirm the terms and amount of any guarantee(s) issued by "
        "your institution on behalf of the account holder."
    ),
    "Derivative": (
        "Please confirm the terms, notional amount, and fair value of any "
        "derivative instrument(s) (e.g., interest rate swap, forward "
        "contract) outstanding with the account holder."
    ),
    "Pledged Collateral": (
        "Please confirm any collateral pledged by the account holder to "
        "secure obligations to your institution, including a description "
        "and estimated value."
    ),
    "Contingent Liability": (
        "Please confirm any contingent liabilities of the account holder "
        "known to your institution not otherwise described above."
    ),
}


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class DraftingBlocked(RuntimeError):
    """Raised when a record has an unresolved Tier 0/Tier 1 issue.
    Drafting refuses outright rather than warning and proceeding."""


class NoTemplateAvailable(RuntimeError):
    """Raised when no jurisdiction/form-type template is registered for a
    record. Never falls back to a generic letter (CLAUDE.md Rule 7)."""


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class DraftedLetter:
    record_reference: str
    template_used: str
    body: str
    recipient_email: str
    confirmation_type: str  # "bank" | "ar" | "legal" | "legal-bring-down" | "intercompany"


@dataclass
class DraftingBatch:
    drafted: list[DraftedLetter] = field(default_factory=list)
    # (sheet, record reference, reason) for anything that could not be drafted.
    blocked: list[tuple[str, str, str]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Template rendering
# ---------------------------------------------------------------------------

_TEMPLATE_CACHE: dict[str, Template] = {}


def _load_template(relpath: str) -> Template:
    if relpath not in _TEMPLATE_CACHE:
        text = (config.TEMPLATES_DIR / relpath).read_text(encoding="utf-8")
        _TEMPLATE_CACHE[relpath] = Template(text)
    return _TEMPLATE_CACHE[relpath]


def _render(relpath: str, context: dict) -> str:
    return _load_template(relpath).substitute(context)


def _format_non_standard_paragraphs(raw_value: object) -> str:
    """Render the Non-Standard Paragraphs Requested multi-select into a
    bulleted request list. A blank value on an Expanded form is a Tier 2
    clarification flag (see intake.py), not a hard gate — this still
    drafts, with an explicit placeholder rather than silently omitting
    the section."""
    text = "" if raw_value is None else str(raw_value).strip()
    if not text:
        return "  - [No non-standard paragraph selected — pending team clarification; see Tier 2 flag.]\n"
    tokens = [t.strip() for t in re.split(r"[;,]", text) if t.strip()]
    lines = []
    for token in tokens:
        if token.upper() == "NONE":
            continue
        request_text = PARAGRAPH_LIBRARY.get(token)
        if request_text is None:
            request_text = "[Team to supply the specific request wording for this non-standard paragraph type.]"
        lines.append(f"  - {token}: {request_text}")
    if not lines:
        return "  - [\"None\" selected — no non-standard paragraphs requested.]\n"
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Blocking-issue gate
# ---------------------------------------------------------------------------

_BLOCKING_TIERS = {rules.TIER_0_ESCALATE, rules.TIER_1_STRUCTURAL}


def _blocking_issues(issues, sheet: str, *reference_candidates: str) -> list:
    """Match a record to its intake issues by EXACT equality against the
    same reference-string conventions intake.py itself builds (e.g.
    "Bank Name / Account Number" for a Tier 1 gate, bare account number
    for a Tier 0 domain flag) — records don't yet have a stable ID, that
    arrives once dispatch.py assigns one. A prior version matched by
    substring on a single field like bank name, which incorrectly
    blocked every account at a bank whenever any one of that bank's
    accounts had an unrelated Tier 1 issue — exact match against the
    full reference string a caller must pass avoids that."""
    candidates = {c.strip().lower() for c in reference_candidates if c}
    if not candidates:
        return []
    return [
        issue
        for issue in issues
        if issue.tier in _BLOCKING_TIERS and issue.sheet == sheet and issue.reference.strip().lower() in candidates
    ]


def _require_no_blocking_issues(issues, sheet: str, *reference_candidates: str) -> None:
    blocking = _blocking_issues(issues, sheet, *reference_candidates)
    if blocking:
        descriptions = "; ".join(f"[{i.tier}] {i.description}" for i in blocking)
        raise DraftingBlocked(f"Unresolved blocking issue(s) for {reference_candidates}: {descriptions}")


# ---------------------------------------------------------------------------
# Drafting
# ---------------------------------------------------------------------------


def draft_bank_letter(row, engagement: dict, issues: list) -> DraftedLetter:
    bank_name = row.get("Bank Name", "")
    account_numbers = row.get("Account Number(s)", "")
    _require_no_blocking_issues(
        issues,
        config.SHEET_BANK,
        f"{bank_name} / {account_numbers}",  # Tier 1 reference convention
        str(account_numbers),  # Tier 0 domain-flag reference convention
    )

    raw_jurisdiction = str(row.get("Jurisdiction / Template Standard", "")).strip()
    try:
        jurisdiction = Jurisdiction(raw_jurisdiction)
    except ValueError as exc:
        raise NoTemplateAvailable(
            f"No template registered for jurisdiction '{raw_jurisdiction}' (account {account_numbers}) — "
            "add it to templates.py's Jurisdiction enum and TEMPLATE_PATHS rather than falling back to a "
            "generic letter (CLAUDE.md Rule 7)."
        ) from exc

    form_type = str(row.get("Confirmation Form Type", "")).strip()
    relpath = TEMPLATE_PATHS.get((jurisdiction, form_type))
    if relpath is None:
        raise NoTemplateAvailable(
            f"No template registered for ({jurisdiction.value}, '{form_type}') — account {account_numbers}."
        )

    context = {
        "confirmation_date": engagement.get("Confirmation Date (Bank)", ""),
        "client_name": engagement.get("Client Name", ""),
        "entity_name": row.get("Entity/Component Name", ""),
        "bank_name": bank_name,
        "account_numbers": account_numbers,
        "currency": row.get("Local Currency", ""),
        "gl_balance": row.get("GL Balance (Local Currency)", ""),
        "auditor_signoff": _auditor_signoff(engagement),
    }
    if form_type == "Expanded":
        context["non_standard_paragraphs"] = _format_non_standard_paragraphs(row.get("Non-Standard Paragraphs Requested"))

    body = _render(relpath, context)
    return DraftedLetter(
        record_reference=f"{bank_name} / {account_numbers}",
        template_used=relpath,
        body=body,
        recipient_email=str(row.get("Bank Contact Email", "")),
        confirmation_type="bank",
    )


def draft_ar_letter(row, engagement: dict, issues: list) -> DraftedLetter:
    customer_name = row.get("Customer Name", "")
    _require_no_blocking_issues(issues, config.SHEET_AR, str(customer_name))

    confirmation_type = str(row.get("Confirmation Type", "")).strip()
    relpath = AR_TEMPLATE_PATHS.get(confirmation_type)
    if relpath is None:
        raise NoTemplateAvailable(f"No AR template registered for Confirmation Type '{confirmation_type}' — {customer_name}.")

    context = {
        "confirmation_date": engagement.get("Confirmation Date (AR)", ""),
        "client_name": engagement.get("Client Name", ""),
        "entity_name": row.get("Entity/Component Name", ""),
        "customer_name": customer_name,
        "currency": row.get("Local Currency", ""),
        "auditor_signoff": _auditor_signoff(engagement),
    }
    # Positive-Blank's template has no $balance placeholder at all — never
    # pass the balance into that render, so a future template edit can't
    # accidentally leak it back in via a stray key.
    if confirmation_type != "Positive-Blank":
        context["balance"] = row.get("GL/Subledger Balance (Local Currency)", "")

    body = _render(relpath, context)
    return DraftedLetter(
        record_reference=customer_name,
        template_used=relpath,
        body=body,
        recipient_email=str(row.get("Customer Contact Email", "")),
        confirmation_type="ar",
    )


def draft_legal_letter(
    row,
    engagement: dict,
    issues: list,
    *,
    is_bring_down: bool = False,
    original_letter_date: str | None = None,
) -> DraftedLetter:
    law_firm_name = row.get("Law Firm Name", "")
    matter_description = row.get("Matter Description", "")
    _require_no_blocking_issues(issues, config.SHEET_LEGAL, f"{law_firm_name} / {matter_description}")

    if is_bring_down and not original_letter_date:
        raise ValueError(
            "original_letter_date is required for a bring-down letter — pass the date the original letter "
            "was dispatched (from the tracker, once dispatch.py/tracking.py exist)."
        )

    context = {
        "confirmation_date": engagement.get("Confirmation Date (Legal)", ""),
        "client_name": engagement.get("Client Name", ""),
        "entity_name": row.get("Entity/Component Name", ""),
        "law_firm_name": law_firm_name,
        "matter_description": matter_description,
        "period_end_date": engagement.get("Period-End Date", ""),
        "auditor_signoff": _auditor_signoff(engagement),
    }

    if is_bring_down:
        relpath = LEGAL_TEMPLATE_PATHS["bring_down"]
        context["original_letter_date"] = original_letter_date
    else:
        relpath = LEGAL_TEMPLATE_PATHS["standard"]
        context["assertion_status"] = row.get("Asserted / Unasserted / N-A", "")
        context["managements_assessment"] = row.get("Management's Assessment", "")
        exposure = row.get("Estimated Exposure (Local Currency)", "")
        currency = row.get("Local Currency", "")
        context["exposure"] = f"{currency} {exposure}".strip() if exposure not in (None, "") else "Unable to estimate"
        context["currency"] = currency
        context["unbilled_fees"] = row.get("Unbilled/Unpaid Fees at Period-End (Local Currency)", "")

    body = _render(relpath, context)
    return DraftedLetter(
        record_reference=f"{law_firm_name} / {matter_description}",
        template_used=relpath,
        body=body,
        recipient_email=str(row.get("Law Firm Contact Email", "")),
        confirmation_type="legal-bring-down" if is_bring_down else "legal",
    )


def draft_intercompany_requests(row, engagement: dict, issues: list) -> list[DraftedLetter]:
    """Intercompany is a two-sided *internal* data request, not a
    third-party confirmation letter (io-spec.md 1.5) — one draft per
    component, each asking that component to state its own side. Neither
    side's contact email is captured on the Intercompany Balance
    Agreement tab, so recipient_email is left blank with an explicit note
    in the body; the team must supply the internal contact before
    dispatch."""
    component_a = row.get("Component A", "")
    component_b = row.get("Component B", "")
    _require_no_blocking_issues(issues, config.SHEET_INTERCOMPANY, f"{component_a} / {component_b}")

    base_context = {
        "confirmation_date": engagement.get("Confirmation Date (AR)", engagement.get("Period-End Date", "")),
        "period_end_date": engagement.get("Period-End Date", ""),
        "component_a": component_a,
        "component_b": component_b,
        "nature_of_balance": row.get("Nature of Balance", ""),
        "auditor_signoff": _auditor_signoff(engagement),
    }

    sides = [
        (component_a, component_b, row.get("Component A Balance", ""), row.get("Currency A", "")),
        (component_b, component_a, row.get("Component B Balance", ""), row.get("Currency B", "")),
    ]

    drafts = []
    for recipient_component, counterparty_component, balance, currency in sides:
        context = dict(
            base_context,
            recipient_component=recipient_component,
            counterparty_component=counterparty_component,
            recipient_balance=balance,
            recipient_currency=currency,
        )
        body = _render(INTERCOMPANY_TEMPLATE_PATH, context)
        drafts.append(
            DraftedLetter(
                record_reference=f"{component_a} / {component_b} ({recipient_component} side)",
                template_used=INTERCOMPANY_TEMPLATE_PATH,
                body=body,
                recipient_email="",
                confirmation_type="intercompany",
            )
        )
    return drafts


def _auditor_signoff(engagement: dict) -> str:
    partner = engagement.get("Engagement Partner", "")
    return f"Please direct correspondence to the audit team.\n{partner}\nEngagement Partner"


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def draft_all(intake_result) -> DraftingBatch:
    """Draft every record in an IntakeResult. Records with an unresolved
    Tier 0/Tier 1 issue, or an unmapped jurisdiction/form-type/
    confirmation-type, are collected in .blocked rather than raising —
    one bad record must not stop the whole run."""
    batch = DraftingBatch()
    engagement = intake_result.engagement
    issues = intake_result.issues

    for _, row in intake_result.bank.iterrows():
        ref = f"{row.get('Bank Name', '')} / {row.get('Account Number(s)', '')}"
        try:
            batch.drafted.append(draft_bank_letter(row, engagement, issues))
        except (DraftingBlocked, NoTemplateAvailable) as exc:
            batch.blocked.append((config.SHEET_BANK, ref, str(exc)))

    for _, row in intake_result.ar.iterrows():
        ref = str(row.get("Customer Name", ""))
        try:
            batch.drafted.append(draft_ar_letter(row, engagement, issues))
        except (DraftingBlocked, NoTemplateAvailable) as exc:
            batch.blocked.append((config.SHEET_AR, ref, str(exc)))

    for _, row in intake_result.legal.iterrows():
        ref = f"{row.get('Law Firm Name', '')} / {row.get('Matter Description', '')}"
        try:
            batch.drafted.append(draft_legal_letter(row, engagement, issues))
            if str(row.get("Bring-Down Letter Required?", "")).strip().upper() == "Y":
                # No dispatch tracker exists yet (Step 3) to source the actual
                # sent date, so the original confirmation date stands in —
                # replace with the tracker's real sent date once dispatch.py
                # and tracking.py exist.
                batch.drafted.append(
                    draft_legal_letter(
                        row,
                        engagement,
                        issues,
                        is_bring_down=True,
                        original_letter_date=engagement.get("Confirmation Date (Legal)", ""),
                    )
                )
        except (DraftingBlocked, NoTemplateAvailable) as exc:
            batch.blocked.append((config.SHEET_LEGAL, ref, str(exc)))

    for _, row in intake_result.intercompany.iterrows():
        ref = f"{row.get('Component A', '')} / {row.get('Component B', '')}"
        try:
            batch.drafted.extend(draft_intercompany_requests(row, engagement, issues))
        except (DraftingBlocked, NoTemplateAvailable) as exc:
            batch.blocked.append((config.SHEET_INTERCOMPANY, ref, str(exc)))

    return batch


def summarize_drafting(batch: DraftingBatch) -> str:
    lines = ["Confirmation Management Agent — Drafting Summary (Step 2)", "=" * 58]
    by_type: dict[str, int] = {}
    for d in batch.drafted:
        by_type[d.confirmation_type] = by_type.get(d.confirmation_type, 0) + 1
    lines.append(f"Drafted: {len(batch.drafted)} " + ", ".join(f"{k}={v}" for k, v in sorted(by_type.items())))
    lines.append(f"Blocked (unresolved Tier 0/Tier 1 issue or unmapped template): {len(batch.blocked)}")
    for sheet, ref, reason in batch.blocked:
        lines.append(f"  - [{sheet}] {ref}: {reason}")
    return "\n".join(lines)
