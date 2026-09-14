"""
Confirmation Management Agent — business-rule defaults.

Everything here is a FALLBACK ONLY. The authoritative values for a given
engagement always come from the "Engagement Setup" tab of the input
workbook (docs/io-spec.md Section 1.1) — nothing in this file should be
treated as a hardcoded engagement decision. Kept separate from config.py
(which only answers "where/how is the workbook laid out") so a reviewer
can see every audit-judgment-adjacent default in one place.
"""

from dataclasses import dataclass


@dataclass
class Tolerances:
    bank_absolute: float = 500.0
    bank_pct: float = 0.005
    ar_absolute: float = 250.0
    ar_pct: float = 0.01
    intercompany_absolute: float = 1000.0
    intercompany_pct: float = 0.01


@dataclass
class Cadence:
    """Business-day chase intervals. Negative AR confirmations are never
    chased regardless of these values — see docs/workflow-skill.md Section 5
    and chase.py's is_chase_eligible()."""
    bank_ar_first: int = 10
    bank_ar_second: int = 20
    bank_ar_escalate: int = 30
    legal_first: int = 25
    legal_escalate: int = 40


DEFAULT_TOLERANCES = Tolerances()
DEFAULT_CADENCE = Cadence()

# ---------------------------------------------------------------------------
# Flag tiers — see docs/io-spec.md Section 7
# ---------------------------------------------------------------------------
TIER_0_ESCALATE = "Tier 0 — Immediate Escalation"
TIER_1_STRUCTURAL = "Tier 1 — Structural"
TIER_2_GRADUATED = "Tier 2 — Graduated"
