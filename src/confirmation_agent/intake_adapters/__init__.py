"""
Client intake adapters.

The canonical input schema lives in docs/io-spec.md and is mirrored in
schemas.py / config.py — every downstream module (validation, templates,
tracking, reconciliation) relies on that exact shape. A real client's
workbook will not always match it: different tab names, a different
header-row offset, renamed columns.

Rather than loosening validation in intake.py to "guess" at variant
layouts — which risks silently misreading a renamed column and either
producing a false Tier 1 gate or, worse, missing a real one (see
CLAUDE.md's "Tab/column name drift" known failure mode) — each client
gets an explicit, reviewable AdapterSpec that maps their workbook's
actual layout onto the canonical one *before* intake.py's validation
logic ever runs. schemas.py and io-spec.md stay the single source of
truth; the adapter is the only place that knows a given client's raw
export looks different.

To add a new client:
  1. Copy example_client.py, rename the file and the AdapterSpec.name.
  2. Fill in only the sheet_names / header_rows / column_map /
     engagement_field_map entries that actually differ for that client
     — leave everything else out, since load_all() falls back to the
     canonical config.py/schemas.py values wherever an adapter doesn't
     override them.
  3. Register the instance in ADAPTERS below.
  4. Run `confirmation-agent --input <their file> --adapter <name>` and
     refine the mapping until the Tier 1 structural-gate count matches
     what a human reviewer expects from that workbook — not necessarily
     zero (real missing data should still be flagged), just no
     *spurious* gates caused by a column the adapter forgot to map.
"""

from __future__ import annotations

from .base import AdapterSpec
from .example_client import EXAMPLE_CLIENT_ADAPTER

ADAPTERS: dict[str, AdapterSpec] = {
    EXAMPLE_CLIENT_ADAPTER.name: EXAMPLE_CLIENT_ADAPTER,
}


def get_adapter(name: str | None) -> AdapterSpec | None:
    """Resolve a registered adapter by name. None in, None out — callers
    use that to mean 'this workbook already matches the canonical
    io-spec.md format, no normalization needed'."""
    if name is None:
        return None
    try:
        return ADAPTERS[name]
    except KeyError:
        available = ", ".join(sorted(ADAPTERS)) or "(none registered)"
        raise KeyError(f"No intake adapter named '{name}'. Registered adapters: {available}") from None


def list_adapters() -> list[str]:
    return sorted(ADAPTERS)
