"""
Column-level schemas for every input tab.

These MUST mirror docs/io-spec.md Section 1 exactly. If the input
workbook's column headers ever change, update io-spec.md first, then
this file, then re-run tests/test_intake.py.
"""

# ---------------------------------------------------------------------------
# Bank Confirmation Population (io-spec.md 1.2)
# ---------------------------------------------------------------------------
BANK_COLUMNS = [
    "Entity/Component Name",
    "Jurisdiction / Template Standard",
    "Bank Name",
    "Bank Contact Email",
    "Account Number(s)",
    "GL Balance (Local Currency)",
    "Local Currency",
    "Confirmation Form Type",
    "Non-Standard Paragraphs Requested",
    "Prior-Year Exception?",
    "Related Party? (self-reported)",
    "Intercompany?",
]
BANK_REQUIRED = [
    "Entity/Component Name",
    "Jurisdiction / Template Standard",
    "Bank Name",
    "Bank Contact Email",
    "Account Number(s)",
    "GL Balance (Local Currency)",
    "Local Currency",
    "Confirmation Form Type",
]

# ---------------------------------------------------------------------------
# AR Confirmation Population (io-spec.md 1.3)
# ---------------------------------------------------------------------------
AR_COLUMNS = [
    "Entity/Component Name",
    "Customer Name",
    "Customer Contact Email",
    "GL/Subledger Balance (Local Currency)",
    "Local Currency",
    "Confirmation Type",
    "Threshold Rule Applied",
    "Related Party? (self-reported)",
    "Prior-Year Exception?",
    "Intercompany?",
]
AR_REQUIRED = [
    "Entity/Component Name",
    "Customer Name",
    "Customer Contact Email",
    "GL/Subledger Balance (Local Currency)",
    "Local Currency",
    "Confirmation Type",
]
AR_NEGATIVE_VALUE = "Negative"  # confirmation types that follow the non-chased track

# ---------------------------------------------------------------------------
# Legal Confirmation Population (io-spec.md 1.4)
# ---------------------------------------------------------------------------
LEGAL_COLUMNS = [
    "Entity/Component Name",
    "Law Firm Name",
    "Law Firm Contact Email",
    "Matter Description",
    "Asserted / Unasserted / N-A",
    "Estimated Exposure (Local Currency)",
    "Local Currency",
    "Management's Assessment",
    "Unbilled/Unpaid Fees at Period-End (Local Currency)",
    "Substantive Attention Confirmed?",
    "Bring-Down Letter Required?",
    "Prior-Year Response Type",
]
LEGAL_REQUIRED = [
    "Entity/Component Name",
    "Law Firm Name",
    "Law Firm Contact Email",
    "Matter Description",
    "Asserted / Unasserted / N-A",
]

# ---------------------------------------------------------------------------
# Intercompany Balance Agreement (io-spec.md 1.5)
# ---------------------------------------------------------------------------
INTERCOMPANY_COLUMNS = [
    "Component A",
    "Component A Balance",
    "Currency A",
    "Component B",
    "Component B Balance",
    "Currency B",
    "Nature of Balance",
    "Elimination Reference",
]
INTERCOMPANY_REQUIRED = [
    "Component A",
    "Component A Balance",
    "Currency A",
    "Component B",
    "Component B Balance",
    "Currency B",
]

# ---------------------------------------------------------------------------
# GL / Subledger Extract (io-spec.md 1.6)
# ---------------------------------------------------------------------------
GL_COLUMNS = [
    "Entity/Component Name",
    "Account/Customer/Matter Reference",
    "GL Balance as of Confirmation Date",
    "GL Balance as of Period-End",
    "Local Currency",
]

# ---------------------------------------------------------------------------
# Related Party List (io-spec.md 1.7)
# ---------------------------------------------------------------------------
RELATED_PARTY_COLUMNS = ["Entity", "Related Party Name", "Relationship", "Source"]

# ---------------------------------------------------------------------------
# Engagement Setup (io-spec.md 1.1) — Field/Value sheet, not a flat table
# ---------------------------------------------------------------------------
ENGAGEMENT_SETUP_REQUIRED_FIELDS = [
    "Client Name",
    "Engagement Code",
    "Period-End Date",
    "Group Reporting Currency",
    "Group Materiality",
    "FX Rate Source & Convention",
]
