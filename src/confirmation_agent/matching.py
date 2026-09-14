"""
Matching utilities shared across the pipeline.

Everything here PROPOSES a match or flags a discrepancy — it never
silently merges records or auto-resolves an identity question. See
docs/workflow-skill.md Section 6 ("Complex-Scenario & Exception
Flagging") and Section 4 (Tier 0 domain screening).
"""

from __future__ import annotations

import difflib
import re
from collections import Counter
from dataclasses import dataclass


def extract_domain(email: str) -> str | None:
    """Return the lowercase domain of an email address, or None if the
    value isn't a usable email (missing, blank, malformed)."""
    if not isinstance(email, str) or "@" not in email:
        return None
    return email.strip().lower().split("@", 1)[1]


@dataclass
class DomainFlag:
    bank_name: str
    expected_domain: str
    observed_domain: str
    account_ref: str
    similarity: float


def flag_lookalike_domains(bank_df, bank_name_col: str, email_col: str, account_col: str) -> list[DomainFlag]:
    """
    Tier 0 check: for each Bank Name appearing more than once in the
    population, treat the most common contact-email domain as the
    'expected' domain for that bank. Any row using a different domain
    is flagged — with a similarity score so a genuine look-alike
    (e.g. ct-bank-secure.com vs. ctbank.com) is distinguishable from an
    unrelated department address at a glance, without deciding which
    is correct. A human confirms; this function only proposes.
    """
    flags: list[DomainFlag] = []
    domains_by_bank: dict[str, list[str]] = {}

    for _, row in bank_df.iterrows():
        domain = extract_domain(row.get(email_col))
        if domain is None:
            continue
        domains_by_bank.setdefault(row[bank_name_col], []).append(domain)

    expected_domain_by_bank = {
        bank: Counter(domains).most_common(1)[0][0]
        for bank, domains in domains_by_bank.items()
        if len(domains) > 0
    }

    for _, row in bank_df.iterrows():
        bank = row[bank_name_col]
        domain = extract_domain(row.get(email_col))
        if domain is None or bank not in expected_domain_by_bank:
            continue
        expected = expected_domain_by_bank[bank]
        if domain != expected:
            similarity = difflib.SequenceMatcher(None, domain, expected).ratio()
            flags.append(
                DomainFlag(
                    bank_name=bank,
                    expected_domain=expected,
                    observed_domain=domain,
                    account_ref=str(row.get(account_col, "")),
                    similarity=round(similarity, 3),
                )
            )
    return flags


def normalize_name(name: str) -> str:
    """Lowercase, strip common legal suffixes and punctuation, for
    proposing near-duplicate counterparty matches. Never used to merge
    records automatically — only to group candidates for human review."""
    if not isinstance(name, str):
        return ""
    n = name.lower().strip()
    n = re.sub(r"[.,]", "", n)
    for suffix in (" ltd", " llc", " inc", " co", " corp", " plc", " grp", " group"):
        if n.endswith(suffix):
            n = n[: -len(suffix)].strip()
    n = re.sub(r"\s+", " ", n)
    return n


@dataclass
class NameMatchProposal:
    entity: str
    name_a: str
    name_b: str
    similarity: float


def propose_near_duplicate_names(df, entity_col: str, name_col: str, threshold: float = 0.82) -> list[NameMatchProposal]:
    """Within each entity, propose pairs of counterparty names that are
    likely the same real-world party under a different spelling/suffix.
    Returns proposals for team confirmation — never merges."""
    proposals: list[NameMatchProposal] = []
    for entity, group in df.groupby(entity_col):
        names = sorted(set(group[name_col].dropna().astype(str)))
        normalized = {n: normalize_name(n) for n in names}
        for i, a in enumerate(names):
            for b in names[i + 1 :]:
                if a == b:
                    continue
                ratio = difflib.SequenceMatcher(None, normalized[a], normalized[b]).ratio()
                if ratio >= threshold:
                    proposals.append(NameMatchProposal(entity=entity, name_a=a, name_b=b, similarity=round(ratio, 3)))
    return proposals
