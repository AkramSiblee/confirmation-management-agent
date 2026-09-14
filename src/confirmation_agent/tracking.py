"""
Step 4 — Response Tracking, Matching & Fraud-Indicator Screening.

Ingests responses (manual upload, inbox scan, or e-confirmation platform
export) and matches them to open DispatchRecords. NOT YET IMPLEMENTED,
but the Tier 0 domain-verification logic it depends on already exists
and is tested — see matching.flag_lookalike_domains and
matching.extract_domain.

Status vocabulary (io-spec.md Section 9) — use these exact labels, the
workpaper/presentation layer keys off them:
  - "Outstanding"                              (positive/legal, no reply yet)
  - "Received — Clean"                          (matched, domain-verified, no variance)
  - "Received — Exception"                      (matched, variance beyond tolerance)
  - "Delivered — No Reply (Expected)"           (NEGATIVE confirmations only — never "Outstanding")
  - "Received — Disagreement" (negative only)   (a negative confirmation reply reporting a difference)
  - "Suspense — Unmatched"                      (response received, cannot be matched to a dispatch)

Rule carried over from the spec: a response whose sender domain fails
the Tier 0 check (matching.flag_lookalike_domains logic, applied to the
RESPONSE'S sender address, not just the original request) must be held
in Suspense — never auto-promoted to "Received — Clean" regardless of
how well the stated balance matches.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TrackerRow:
    record_reference: str
    confirmation_type: str
    status: str
    response_artifact_id: str | None = None
    chase_count: int = 0


def ingest_response(raw_response, dispatch_log) -> TrackerRow:
    raise NotImplementedError(
        "1) Extract sender domain from raw_response and re-run the Tier 0 check "
        "against the domain the original request was sent to. "
        "2) Match to an open DispatchRecord by counterparty + balance type. "
        "3) For AR Negative confirmations, a reply is a disagreement report, not a "
        "routine 'received' — route to 'Received — Disagreement', never chase it. "
        "4) Unmatched -> Suspense, never force-matched."
    )


def normalize_econfirmation_export(raw_rows: list[dict]) -> list[TrackerRow]:
    raise NotImplementedError(
        "Native platform status codes (e.g. RESP-RECV, PEND-BANK — see "
        "sample_data workbook's 'E-Confirmation Platform Export' tab for the "
        "shape) must be mapped to the internal status vocabulary above. "
        "Never surface a platform-native code directly in the tracker."
    )
