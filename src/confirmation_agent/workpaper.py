"""
Step 8 — Workpaper & Summary Generation.

NOT YET IMPLEMENTED. Assembles the final Excel deliverable per
docs/io-spec.md Section 6 — one workbook, these tabs in this order:

  1. Cover / Engagement Summary
  2. Bank Tracker
  3. AR Tracker            (Negative rows use the distinct status vocabulary — never "Outstanding")
  4. Legal Tracker
  5. Intercompany Matching
  6. Exception Schedule    (all tiers, standard reference included)
  7. Reconciliation Detail
  8. Unconfirmed / Alternative-Procedures Candidates
  9. Chase Log
  10. Changelog

Formatting standards to carry over (io-spec.md Sections 8-9):
  - Arial font throughout; bold header row with a fill color, matching
    the sample_data workbook's existing visual convention.
  - Status color coding: Outstanding=amber, Received-Clean=green,
    Exception=red, Suspense=grey, Negative-No-Reply=neutral blue.
  - Tier 0 items get a visually distinct marker, separate from routine
    Tier 2 red, so they can't be mistaken for a routine exception.
  - Every translated (FX) figure carries its rate source as a cell
    comment or adjacent note.
  - Reconciliation columns use formulas, not hardcoded results, so a
    reviewer can trace every variance back to its inputs (see the repo's
    root CLAUDE.md for the project's general xlsx-output conventions).

Use openpyxl directly (see build script pattern already proven in this
project's original input-package generation) rather than pandas.to_excel,
so formatting and formulas are controllable per cell.
"""

from __future__ import annotations

from pathlib import Path

from . import config


def build_workpaper(intake_result, tracker_state, exceptions, reconciliations, out_path: Path = None) -> Path:
    out_path = out_path or (config.OUTPUTS_DIR / f"{intake_result.engagement.get('Engagement Code', 'engagement')}_Confirmation_Workpaper.xlsx")
    raise NotImplementedError(
        "Build each tab per the docstring's structure and io-spec.md Section 6. "
        "Recalculate with LibreOffice headless (or the project's recalc convention) "
        "before treating the file as final — see CLAUDE.md."
    )
