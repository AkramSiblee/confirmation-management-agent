"""
Step 7 — Reconciliation to GL/Subledger (and Intercompany Matching).

NOT YET IMPLEMENTED. Reconciles confirmed balances to
sample_data's "GL_Subledger Extract" tab, and independently reconciles
each side of every row in "Intercompany Balance Agreement".

Rules carried over from the spec (docs/workflow-skill.md Step 7;
io-spec.md Sections 3 & 7):
  1. Reconcile in LOCAL currency first, always. Never compare two
     already-translated figures as if that were the primary check.
  2. Every translated figure must cite config's FX Rate Source (pull it
     from IntakeResult.engagement["FX Rate Source & Convention"]) —
     an unsourced translation is a Tier 1 hard gate on that record, not
     a number to just print.
  3. Where Rollforward Required = Y (bank population), use BOTH GL
     Balance as of Confirmation Date and as of Period-End — a static
     two-number compare against only one of them is wrong.
  4. An FX-driven gap (local currency ties, translated figures don't)
     must be labeled distinctly from a true balance discrepancy.
  5. Intercompany: reconcile Component A's and Component B's balances
     each in their own local currency against their own subledger
     first (if available), THEN compute the cross-entity variance net
     of the FX-timing effect — see the sample workbook's three
     Intercompany Balance Agreement rows for the shape of what a
     genuine gap (loan, management fee) vs. a clean tie (cross-shipment)
     looks like once correctly translated.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ReconciliationResult:
    record_reference: str
    local_currency_variance: float
    translated_variance: float | None
    fx_rate_source: str
    is_fx_only_variance: bool
    within_tolerance: bool


def reconcile_bank_or_ar(population_row, gl_row, tolerance, fx_rate_source: str) -> ReconciliationResult:
    raise NotImplementedError("See module docstring, rules 1-4.")


def reconcile_intercompany(ic_row, fx_rate_source: str, tolerance) -> ReconciliationResult:
    raise NotImplementedError("See module docstring, rule 5.")
