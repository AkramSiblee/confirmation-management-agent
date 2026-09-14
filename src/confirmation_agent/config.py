"""
Confirmation Management Agent — I/O layout configuration.

Where things live and how the workbook is shaped: paths, sheet names,
and header-row offsets. Business-rule defaults (tolerances, cadence,
flag tiers) live in rules.py, not here — this file only ever answers
"where is it / how is it laid out", never "what should happen".
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DATA_DIR = PROJECT_ROOT / "sample_data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
DEFAULT_SAMPLE_WORKBOOK = SAMPLE_DATA_DIR / "confirmation-management-input-package.xlsx"

# ---------------------------------------------------------------------------
# Sheet names — must match the workbook exactly (docs/io-spec.md Section 1)
# ---------------------------------------------------------------------------
SHEET_ENGAGEMENT_SETUP = "Engagement Setup"
SHEET_BANK = "Bank Confirmation Population"
SHEET_AR = "AR Confirmation Population"
SHEET_LEGAL = "Legal Confirmation Population"
SHEET_INTERCOMPANY = "Intercompany Balance Agreement"
SHEET_GL_EXTRACT = "GL_Subledger Extract"
SHEET_RELATED_PARTY = "Related Party List"
SHEET_PRIOR_YEAR = "Prior Year Exceptions"
SHEET_ECONFIRM = "E-Confirmation Platform Export"

# Row (0-indexed, pandas `header=`) where each population tab's column
# header lives. Population tabs are written with a title (row 1), an
# optional subtitle (row 2), and the header row at Excel row 3 -> header=2.
POPULATION_HEADER_ROW = 2

# Engagement Setup is a Field/Value sheet with its header at Excel row 4,
# in columns B:C -> header=3, usecols="B:C".
ENGAGEMENT_SETUP_HEADER_ROW = 3
ENGAGEMENT_SETUP_USECOLS = "B:C"

CONFIRMATION_TYPES = ("bank", "ar", "legal", "intercompany")
