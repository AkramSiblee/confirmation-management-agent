"""
Tests for Step 1 (intake.py), run against the deliberately imperfect
sample workbook in sample_data/. These assert the agent actually catches
every planted issue described in the input-package handoff — not just
that it runs without error.

No sys.path manipulation needed here: pyproject.toml's
[tool.pytest.ini_options] pythonpath = ["src"] makes `confirmation_agent`
importable directly once the package is installed (`pip install -e .`)
or simply run via `pytest` from the repo root.
"""

from confirmation_agent import rules
from confirmation_agent.intake import load_all


def test_loads_all_sheets_with_expected_row_counts():
    result = load_all()
    assert len(result.bank) == 15
    assert len(result.ar) == 19
    assert len(result.legal) == 9
    assert len(result.intercompany) == 3


def test_engagement_setup_parsed():
    result = load_all()
    assert result.engagement["Client Name"] == "Meridian Supply Group"
    assert result.engagement["Engagement Code"] == "MSG-FY25-001"


def test_tier1_missing_contact_emails_caught():
    result = load_all()
    tier1 = result.issues_by_tier(rules.TIER_1_STRUCTURAL)
    # 1 bank + 3 AR + 1 legal = 5 missing-contact-email hard gates planted
    assert len(tier1) == 5
    assert all("Missing required field" in i.description for i in tier1)


def test_literal_na_value_is_not_a_false_missing_gate():
    """The Whitmore Grayson retainer-only row legitimately uses the string
    'N/A' for Asserted/Unasserted — pandas' default NA parsing would
    otherwise misclassify this as a missing-field hard gate."""
    result = load_all()
    tier1_refs = [i.reference for i in result.issues_by_tier(rules.TIER_1_STRUCTURAL)]
    assert not any("General corporate matters" in ref for ref in tier1_refs)


def test_tier0_lookalike_domain_flagged():
    result = load_all()
    tier0 = result.issues_by_tier(rules.TIER_0_ESCALATE)
    assert len(tier0) == 1
    assert "ct-bank-secure.com" in tier0[0].description
    assert tier0[0].reference == "CD-40021"


def test_related_party_self_report_gap_caught():
    result = load_all()
    tier2 = result.issues_by_tier(rules.TIER_2_GRADUATED)
    assert any("Vantage Point Holdings" in i.reference for i in tier2)
    assert any("Northgate Holdings" in i.reference for i in tier2)
    assert any("TL-70044" in i.reference for i in tier2)


def test_blank_expanded_paragraph_flagged():
    result = load_all()
    tier2 = result.issues_by_tier(rules.TIER_2_GRADUATED)
    assert any(i.reference == "LOC-91820" for i in tier2)


def test_near_duplicate_names_proposed_not_merged():
    result = load_all()
    tier2 = result.issues_by_tier(rules.TIER_2_GRADUATED)
    dup_refs = [i.reference for i in tier2 if "<->" in i.reference]
    assert any("Alberta Steel Distributors" in r for r in dup_refs)
    assert any("Redwood Fabrication" in r for r in dup_refs)
    # every row in the AR/Bank frames must still be present and distinct —
    # a "proposal" must never have removed or merged a record
    assert len(result.ar) == 19
    assert len(result.bank) == 15
