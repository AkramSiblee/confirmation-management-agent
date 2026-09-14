"""
AdapterSpec — the shape a client-specific intake adapter fills in.

Every field is optional and additive: leave out anything that already
matches the canonical layout (docs/io-spec.md, config.py, schemas.py).
intake.py falls back to the canonical value for anything not overridden
here, so an adapter only ever needs to encode what's actually different
about one client's export.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AdapterSpec:
    name: str

    # Canonical sheet name (config.SHEET_*) -> actual sheet name in this
    # client's workbook, for any tab whose name differs.
    sheet_names: dict[str, str] = field(default_factory=dict)

    # Canonical sheet name -> header row override (0-indexed, pandas
    # `header=` convention), for any population tab laid out with a
    # different title/subtitle-row convention than
    # config.POPULATION_HEADER_ROW.
    header_rows: dict[str, int] = field(default_factory=dict)

    # Canonical sheet name -> {source column name: canonical column name},
    # for any tab with renamed columns. Only list the columns that differ.
    column_map: dict[str, dict[str, str]] = field(default_factory=dict)

    # Engagement Setup is a Field/Value sheet rather than a flat table —
    # override its header row / usecols if this client's version isn't
    # laid out per config.ENGAGEMENT_SETUP_HEADER_ROW / _USECOLS.
    engagement_setup_header_row: int | None = None
    engagement_setup_usecols: str | None = None

    # Source field label -> canonical field label, for any Engagement
    # Setup field this client names differently (e.g. "Client" instead
    # of "Client Name"). Only list the ones that differ.
    engagement_field_map: dict[str, str] = field(default_factory=dict)

    def sheet_name_for(self, canonical: str) -> str:
        return self.sheet_names.get(canonical, canonical)

    def header_row_for(self, canonical: str, default: int) -> int:
        return self.header_rows.get(canonical, default)

    def columns_for(self, canonical: str) -> dict[str, str]:
        return self.column_map.get(canonical, {})
