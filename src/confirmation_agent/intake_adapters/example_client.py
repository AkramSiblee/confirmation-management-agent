"""
Example adapter — the reference pattern to copy for a real client whose
export doesn't match docs/io-spec.md's canonical layout. Not a real
client; kept in the repo and exercised by tests/test_intake_adapters.py
so the mechanism itself stays covered by the test suite.

Stands in for a client who exports:
  - the Bank tab as "Bank Confo Export" instead of
    "Bank Confirmation Population"
  - that tab's header one row lower than the canonical
    title/subtitle/header convention (config.POPULATION_HEADER_ROW)
  - "Bank" / "Contact Email" / "Acct #" instead of "Bank Name" /
    "Bank Contact Email" / "Account Number(s)"
  - the Engagement Setup field "Client" instead of "Client Name"

Every other sheet and column in this example is assumed to already
match io-spec.md, which is why only these four things are listed —
see base.AdapterSpec's docstring on why an adapter is additive-only.
"""

from __future__ import annotations

from .. import config
from .base import AdapterSpec

EXAMPLE_CLIENT_ADAPTER = AdapterSpec(
    name="example_client",
    sheet_names={
        config.SHEET_BANK: "Bank Confo Export",
    },
    header_rows={
        config.SHEET_BANK: config.POPULATION_HEADER_ROW + 1,
    },
    column_map={
        config.SHEET_BANK: {
            "Bank": "Bank Name",
            "Contact Email": "Bank Contact Email",
            "Acct #": "Account Number(s)",
        },
    },
    engagement_field_map={
        "Client": "Client Name",
    },
)
