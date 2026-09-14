"""
Tests for Step 2 (templates.py), run against the sample workbook (which
covers all three bank jurisdictions, both form types, and all three AR
confirmation types) plus a couple of synthetic edge cases.
"""

from __future__ import annotations

import pytest

from confirmation_agent.intake import load_all
from confirmation_agent.templates import (
    DraftingBlocked,
    NoTemplateAvailable,
    draft_all,
    draft_bank_letter,
    draft_intercompany_requests,
    draft_legal_letter,
)


@pytest.fixture(scope="module")
def intake_result():
    return load_all()


def test_draft_all_matches_known_blocked_and_drafted_counts(intake_result):
    """Regression test for the reference-matching gate: it must block
    exactly the records with a real Tier 0/Tier 1 issue on THAT record —
    not every record sharing a bank/law-firm name with a flagged one
    (see the bug this fixed: substring-matching on "Bank Name" alone
    blocked every account at a bank whenever any one account there had
    an unrelated missing-email gate)."""
    batch = draft_all(intake_result)

    # 15 bank + 19 AR + 9 legal (+4 bring-downs, minus 1 whose base letter
    # is blocked) + 3 intercompany x 2 sides = 46; 1 Tier 0 + 5 Tier 1 = 6 blocked.
    assert len(batch.drafted) == 46
    assert len(batch.blocked) == 6

    blocked_refs = {ref for _, ref, _ in batch.blocked}
    assert "Continental Trust Bank / CD-40021" in blocked_refs  # Tier 0 look-alike domain
    assert "First National Bank / 004-88213" in blocked_refs  # Tier 1 missing email
    # A DIFFERENT First National Bank account with no issues of its own
    # must NOT be caught by the same-bank-name gate.
    assert "First National Bank / 004-88214" not in blocked_refs
    assert "First National Bank / 004-91177" not in blocked_refs


def test_ar_positive_blank_never_shows_the_balance(intake_result):
    batch = draft_all(intake_result)
    thames_balance = str(
        intake_result.ar.loc[intake_result.ar["Customer Name"] == "Thames Retail Group", "GL/Subledger Balance (Local Currency)"].iloc[0]
    )
    draft = next(d for d in batch.drafted if d.confirmation_type == "ar" and "Thames Retail Group" in d.record_reference)
    assert "positive_blank" in draft.template_used
    assert thames_balance not in draft.body
    assert "____" in draft.body  # the blank line the counterparty fills in


def test_bank_jurisdictions_select_distinct_templates(intake_result):
    batch = draft_all(intake_result)
    templates_used = {d.template_used for d in batch.drafted if d.confirmation_type == "bank"}
    # US/UK/Canada must never collapse onto one generic template (CLAUDE.md Rule 7).
    assert any("us_" in t for t in templates_used)
    assert any("uk_" in t for t in templates_used)
    assert any("ca_" in t for t in templates_used)


def test_expanded_form_with_blank_paragraph_still_drafts_with_placeholder(intake_result):
    """LOC-91820: Expanded form, no paragraph selected — a Tier 2
    clarification flag, not a hard gate, so it must still draft."""
    batch = draft_all(intake_result)
    draft = next(d for d in batch.drafted if "LOC-91820" in d.record_reference)
    assert "pending team clarification" in draft.body


def test_unresolved_tier1_issue_blocks_direct_draft_call(intake_result):
    row = intake_result.bank[intake_result.bank["Account Number(s)"] == "004-88213"].iloc[0]
    with pytest.raises(DraftingBlocked):
        draft_bank_letter(row, intake_result.engagement, intake_result.issues)


def test_unrecognized_jurisdiction_raises_not_falls_back(intake_result):
    row = intake_result.bank.iloc[0].copy()
    row["Jurisdiction / Template Standard"] = "Other"
    row["Account Number(s)"] = "TEST-NO-ISSUES-0001"  # avoid tripping the blocking-issue gate
    with pytest.raises(NoTemplateAvailable):
        draft_bank_letter(row, intake_result.engagement, [])


def test_legal_bring_down_requires_original_letter_date(intake_result):
    row = intake_result.legal[intake_result.legal["Bring-Down Letter Required?"].astype(str).str.strip() == "Y"].iloc[0]
    with pytest.raises(ValueError):
        draft_legal_letter(row, intake_result.engagement, intake_result.issues, is_bring_down=True)


def test_intercompany_drafts_both_sides_with_swapped_counterparty(intake_result):
    row = intake_result.intercompany.iloc[0]
    drafts = draft_intercompany_requests(row, intake_result.engagement, intake_result.issues)
    assert len(drafts) == 2
    assert row["Component A"] in drafts[0].record_reference
    assert str(row["Component A Balance"]) in drafts[0].body
    assert str(row["Component B Balance"]) in drafts[1].body
    # Intercompany contact emails aren't in io-spec.md's schema for this tab —
    # never fabricate one.
    assert drafts[0].recipient_email == ""
    assert drafts[1].recipient_email == ""
