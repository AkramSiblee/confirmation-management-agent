"""
Step 1 — Intake & Validation.

Loads the input workbook, validates required fields (Tier 1 structural
gates), cross-references the Related Party List against self-reported
flags, screens bank contact domains for look-alike patterns (Tier 0),
and proposes near-duplicate counterparty matches for team review.

This module is fully implemented and tested against
sample_data/confirmation-management-input-package.xlsx — see
tests/test_intake.py. Steps 2-8 (templates, dispatch, tracking, chase,
exception consolidation, reconciliation, workpaper) are scaffolded in
their own modules and are the next build increment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from . import config, rules, schemas
from .intake_adapters import AdapterSpec, get_adapter
from .matching import flag_lookalike_domains, propose_near_duplicate_names


@dataclass
class ValidationIssue:
    tier: str
    sheet: str
    reference: str
    description: str


@dataclass
class IntakeResult:
    engagement: dict
    bank: pd.DataFrame
    ar: pd.DataFrame
    legal: pd.DataFrame
    intercompany: pd.DataFrame
    gl_extract: pd.DataFrame
    related_parties: pd.DataFrame
    issues: list[ValidationIssue] = field(default_factory=list)

    def issues_by_tier(self, tier: str) -> list[ValidationIssue]:
        return [i for i in self.issues if i.tier == tier]


# IMPORTANT: pandas' default NA-string list includes "N/A", "NA", "NULL",
# "None", etc. Several fields in this workbook use "N/A" as a legitimate
# DATA VALUE (e.g. a retainer-only legal matter with no Asserted/Unasserted
# classification, per io-spec.md 1.4). Reading with pandas' defaults would
# silently turn that into a missing value and produce a false Tier 1 gate.
# keep_default_na=False + na_values=[] disables that substitution; a truly
# blank Excel cell still reads as NaN/empty regardless, so real gaps are
# still caught by the `pd.isna(...) or str(...).strip() == ""` checks below.
_READ_KWARGS = dict(keep_default_na=False, na_values=[])


def load_engagement_setup(path: Path, adapter: AdapterSpec | None = None) -> dict:
    sheet_name = adapter.sheet_name_for(config.SHEET_ENGAGEMENT_SETUP) if adapter else config.SHEET_ENGAGEMENT_SETUP
    header_row = (
        adapter.engagement_setup_header_row
        if adapter and adapter.engagement_setup_header_row is not None
        else config.ENGAGEMENT_SETUP_HEADER_ROW
    )
    usecols = (
        adapter.engagement_setup_usecols
        if adapter and adapter.engagement_setup_usecols is not None
        else config.ENGAGEMENT_SETUP_USECOLS
    )
    df = pd.read_excel(path, sheet_name=sheet_name, header=header_row, usecols=usecols, **_READ_KWARGS)
    df.columns = ["Field", "Value"]
    df = df[df["Field"].astype(str).str.strip() != ""]
    engagement = dict(zip(df["Field"], df["Value"]))
    if adapter and adapter.engagement_field_map:
        for source_field, canonical_field in adapter.engagement_field_map.items():
            if source_field in engagement:
                engagement[canonical_field] = engagement.pop(source_field)
    return engagement


def _load_sheet(path: Path, canonical_sheet_name: str, adapter: AdapterSpec | None = None) -> pd.DataFrame:
    sheet_name = adapter.sheet_name_for(canonical_sheet_name) if adapter else canonical_sheet_name
    header_row = (
        adapter.header_row_for(canonical_sheet_name, config.POPULATION_HEADER_ROW)
        if adapter
        else config.POPULATION_HEADER_ROW
    )
    df = pd.read_excel(path, sheet_name=sheet_name, header=header_row, **_READ_KWARGS)
    if adapter:
        rename = adapter.columns_for(canonical_sheet_name)
        if rename:
            df = df.rename(columns=rename)
    return df


def load_all(path: Path | str = config.DEFAULT_SAMPLE_WORKBOOK, adapter: AdapterSpec | str | None = None) -> IntakeResult:
    path = Path(path)
    if isinstance(adapter, str):
        adapter = get_adapter(adapter)
    engagement = load_engagement_setup(path, adapter)
    bank = _load_sheet(path, config.SHEET_BANK, adapter)
    ar = _load_sheet(path, config.SHEET_AR, adapter)
    legal = _load_sheet(path, config.SHEET_LEGAL, adapter)
    intercompany = _load_sheet(path, config.SHEET_INTERCOMPANY, adapter)
    gl_extract = _load_sheet(path, config.SHEET_GL_EXTRACT, adapter)
    related_parties = _load_sheet(path, config.SHEET_RELATED_PARTY, adapter)

    result = IntakeResult(
        engagement=engagement,
        bank=bank,
        ar=ar,
        legal=legal,
        intercompany=intercompany,
        gl_extract=gl_extract,
        related_parties=related_parties,
    )
    _validate_required_fields(result)
    _cross_check_related_parties(result)
    _screen_bank_domains(result)
    _flag_blank_expanded_paragraphs(result)
    _propose_duplicate_names(result)
    return result


def _row_ref(row, *cols) -> str:
    return " / ".join(str(row.get(c, "")) for c in cols)


def _validate_required_fields(result: IntakeResult) -> None:
    checks = [
        (config.SHEET_BANK, result.bank, schemas.BANK_REQUIRED, ["Bank Name", "Account Number(s)"]),
        (config.SHEET_AR, result.ar, schemas.AR_REQUIRED, ["Customer Name"]),
        (config.SHEET_LEGAL, result.legal, schemas.LEGAL_REQUIRED, ["Law Firm Name", "Matter Description"]),
        (config.SHEET_INTERCOMPANY, result.intercompany, schemas.INTERCOMPANY_REQUIRED, ["Component A", "Component B"]),
    ]
    for sheet_name, df, required_cols, ref_cols in checks:
        for idx, row in df.iterrows():
            missing = [c for c in required_cols if pd.isna(row.get(c)) or str(row.get(c)).strip() == ""]
            if missing:
                result.issues.append(
                    ValidationIssue(
                        tier=rules.TIER_1_STRUCTURAL,
                        sheet=sheet_name,
                        reference=_row_ref(row, *ref_cols),
                        description=f"Missing required field(s): {', '.join(missing)}",
                    )
                )


def _cross_check_related_parties(result: IntakeResult) -> None:
    """Self-reported 'N' is never taken as conclusive — cross-check
    every counterparty name against the independent Related Party List."""
    known_related = set(result.related_parties["Related Party Name"].dropna().astype(str).str.strip().str.lower())

    for sheet_name, df, name_col, flag_col in (
        (config.SHEET_BANK, result.bank, "Bank Name", "Related Party? (self-reported)"),
        (config.SHEET_AR, result.ar, "Customer Name", "Related Party? (self-reported)"),
    ):
        for idx, row in df.iterrows():
            name = str(row.get(name_col, "")).strip().lower()
            self_reported = str(row.get(flag_col, "")).strip().upper()
            if name in known_related and self_reported != "Y":
                result.issues.append(
                    ValidationIssue(
                        tier=rules.TIER_2_GRADUATED,
                        sheet=sheet_name,
                        reference=str(row.get(name_col)),
                        description=(
                            "Appears on the independent Related Party List but self-reported "
                            f"as '{self_reported or 'blank'}' in the population — verify relationship."
                        ),
                    )
                )
    # Also check bank population for a related party referenced indirectly
    # (e.g. a personal guarantor named in the Related Party List for an
    # account whose self-reported flag is 'N').
    for idx, row in result.bank.iterrows():
        acct = str(row.get("Account Number(s)", ""))
        self_reported = str(row.get("Related Party? (self-reported)", "")).strip().upper()
        matches = result.related_parties[
            result.related_parties["Relationship"].astype(str).str.contains(acct, na=False)
        ]
        if not matches.empty and self_reported != "Y":
            for _, rp_row in matches.iterrows():
                result.issues.append(
                    ValidationIssue(
                        tier=rules.TIER_2_GRADUATED,
                        sheet=config.SHEET_BANK,
                        reference=acct,
                        description=(
                            f"Related Party List references this account ({rp_row['Related Party Name']}: "
                            f"{rp_row['Relationship']}) but self-reported flag is "
                            f"'{self_reported or 'blank'}' — verify relationship."
                        ),
                    )
                )


def _screen_bank_domains(result: IntakeResult) -> None:
    flags = flag_lookalike_domains(
        result.bank,
        bank_name_col="Bank Name",
        email_col="Bank Contact Email",
        account_col="Account Number(s)",
    )
    for f in flags:
        result.issues.append(
            ValidationIssue(
                tier=rules.TIER_0_ESCALATE,
                sheet=config.SHEET_BANK,
                reference=f.account_ref,
                description=(
                    f"Contact domain '{f.observed_domain}' for {f.bank_name} does not match this "
                    f"bank's expected domain '{f.expected_domain}' (similarity {f.similarity}). "
                    "Escalate to senior/manager before drafting or sending — do not treat as a routine gap."
                ),
            )
        )


def _flag_blank_expanded_paragraphs(result: IntakeResult) -> None:
    for idx, row in result.bank.iterrows():
        form_type = str(row.get("Confirmation Form Type", "")).strip()
        paragraphs = row.get("Non-Standard Paragraphs Requested")
        is_blank = pd.isna(paragraphs) or str(paragraphs).strip() == ""
        if form_type == "Expanded" and is_blank:
            result.issues.append(
                ValidationIssue(
                    tier=rules.TIER_2_GRADUATED,
                    sheet=config.SHEET_BANK,
                    reference=str(row.get("Account Number(s)", "")),
                    description=(
                        "Expanded form selected but no non-standard paragraph specified — "
                        "clarify with the team before drafting; do not assume 'None'."
                    ),
                )
            )


def _propose_duplicate_names(result: IntakeResult) -> None:
    for sheet_name, df, name_col in (
        (config.SHEET_AR, result.ar, "Customer Name"),
        (config.SHEET_BANK, result.bank, "Bank Name"),
    ):
        proposals = propose_near_duplicate_names(df, entity_col="Entity/Component Name", name_col=name_col)
        for p in proposals:
            result.issues.append(
                ValidationIssue(
                    tier=rules.TIER_2_GRADUATED,
                    sheet=sheet_name,
                    reference=f"{p.name_a}  <->  {p.name_b}",
                    description=(
                        f"Proposed near-duplicate counterparty within {p.entity} "
                        f"(similarity {p.similarity}) — confirm with team before treating as one party."
                    ),
                )
            )


def summarize(result: IntakeResult) -> str:
    lines = ["Confirmation Management Agent — Intake Summary", "=" * 48]
    lines.append(f"Client: {result.engagement.get('Client Name', '(unknown)')}")
    lines.append(f"Engagement Code: {result.engagement.get('Engagement Code', '(unknown)')}")
    lines.append(
        f"Population sizes — Bank: {len(result.bank)}, AR: {len(result.ar)}, "
        f"Legal: {len(result.legal)}, Intercompany: {len(result.intercompany)}"
    )
    lines.append("")
    for tier in (rules.TIER_0_ESCALATE, rules.TIER_1_STRUCTURAL, rules.TIER_2_GRADUATED):
        tier_issues = result.issues_by_tier(tier)
        lines.append(f"{tier} ({len(tier_issues)})")
        for issue in tier_issues:
            lines.append(f"  - [{issue.sheet}] {issue.reference}: {issue.description}")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    res = load_all()
    print(summarize(res))
