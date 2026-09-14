---
name: confirmation-management-agent-io-spec
description: Column-level input schemas, output artifact structure, flagging framework, and pre-delivery checklist for the Confirmation Management Agent — bank, AR, legal, and intercompany balance agreement, across multi-jurisdiction group audits
---

# Confirmation Management Agent — IO Spec

## 1. Input File Schemas

### 1.1 Engagement Setup (single tab)

| Column | Type | Required | Notes |
|---|---|---|---|
| Client Name | Text | Y | |
| Engagement Code | Text | Y | Ties to GL extract and prior-year files |
| Period-End Date | Date | Y | |
| Confirmation Date — Bank / AR / Legal | Date (x3) | Y | May precede period-end for bank; if so, Rollforward Required = Y |
| Rollforward Required — Bank / AR | Y/N (x2) | Y (system-set) | Auto-flag if Confirmation Date < Period-End Date |
| Group Reporting Currency | ISO code | Y | Consolidation currency |
| **Component Reporting Framework** | Per entity: AU-C(US GAAS) / PCAOB / ISA / CAS | Y | Drives which standard (AU-C 505, ISA 505, CAS 505) and which contingency framework (ASC 450 vs. IAS 37) governs that entity's confirmations |
| **Group Materiality** | Number (group currency) | Y | |
| **Component Materiality** | Number, per component | Y | Per ISA 600 (Revised)/AU-C 600 — may differ from and be lower than a simple pro-rata share of group materiality |
| Variance Tolerance — Bank / AR | % or absolute (x2) | Y | Graduated flag threshold |
| **FX Rate Source & Convention** | Text | Y | e.g., "Bank of Canada noon rate, confirmation-date and period-end spot" — every translated figure in the output must cite this |
| Chase Cadence — Bank/AR (days) | Number, Number | Y | Default 10 / 20; **does not apply to negative confirmations** |
| Chase Cadence — Legal (days) | Number | Y | Default longer; team-set |
| **Bring-Down Letter Cutoff** | Date | N | If set, legal matters open past this date trigger a second, shorter update letter near the audit report date |
| Engagement Partner / Manager / EQCR | Text (x3) | Y (Partner/Manager); N (EQCR) | EQCR named only where the engagement requires one |
| Group Audit? | Y/N | Y | If Y, expects multiple components below |
| **Data Protection Note** | Text | N | Flags UK GDPR or other cross-border data-handling requirements triggered by counterparty domicile |

### 1.2 Bank Confirmation Population

| Column | Type | Required | Notes |
|---|---|---|---|
| Entity/Component Name | Text | Y | Ties to Engagement Setup if group audit |
| **Jurisdiction / Template Standard** | Enum: US-AICPA/ABA/BAI / UK-ICAEW / CA-CPACanada / Other | Y | Drives Step 2 template selection — never one generic template group-wide |
| Bank Name | Text | Y | |
| Bank Contact Email | Text | Y | Hard gate if missing; domain compared against known counterparty domain at response time (Section 7, Tier 0) |
| Account Number(s) | Text | Y | May be multiple, semicolon-separated |
| GL Balance (Local Currency) | Number | Y | May be negative for a derivative liability position |
| Local Currency | ISO code | Y | |
| Confirmation Form Type | Enum: Standard / Expanded | Y | |
| Non-Standard Paragraphs Requested | Multi-select: Compensating Balance / LOC / Guarantee / Derivative / Pledged Collateral / Contingent Liability / None | N | Drives which paragraphs must be present in a "clean" response; blank on an Expanded form is a clarification flag, never assumed "None" |
| Prior-Year Exception? | Y/N | N | Carries forward context |
| Related Party? (self-reported) | Y/N | N | **Cross-checked against the independent Related Party List — self-reported N is not treated as conclusive** |
| **Intercompany?** | Y/N | N | If Y, also expected on the Intercompany Balance Agreement tab from the counterparty component's side |

### 1.3 AR Confirmation Population

| Column | Type | Required | Notes |
|---|---|---|---|
| Entity/Component Name | Text | Y | |
| Customer Name | Text | Y | Near-duplicate names surfaced as a proposed match, never auto-merged |
| Customer Contact Email | Text | Y | Hard gate if missing |
| GL/Subledger Balance (Local Currency) | Number | Y | |
| Local Currency | ISO code | Y | |
| Confirmation Type | Enum: Positive-Standard / Positive-Blank / Negative | Y | Drives the response-tracking lifecycle — Negative follows the distinct non-chased track (Section 7) |
| Threshold Rule Applied | Text (reference to team's selection rule) | Y | Agent applies, does not set; a balance outside the stated rule's stated range is flagged for clarification, not silently accepted |
| Related Party? (self-reported) | Y/N | N | Cross-checked against Related Party List |
| Prior-Year Exception? | Y/N | N | |
| **Intercompany?** | Y/N | N | See 1.5 |

### 1.4 Legal Confirmation Population

| Column | Type | Required | Notes |
|---|---|---|---|
| Entity/Component Name | Text | Y | |
| Law Firm Name | Text | Y | |
| Law Firm Contact Email | Text | Y | Hard gate if missing |
| Matter Description | Text | Y | |
| Asserted / Unasserted / N/A | Enum | Y | N/A permitted for a retainer-only line with no active litigation |
| Estimated Exposure (Local Currency) | Number or "Unable to estimate" | N | May be genuinely unestimable — not a gate |
| Local Currency | ISO code | N | |
| Management's Assessment | Enum, framework-dependent | Y | ASC 450 entities: Probable/Reasonably Possible/Remote. IAS 37 entities: Probable/Possible/Remote — **the enum used must match the entity's Component Reporting Framework** |
| **Unbilled/Unpaid Fees at Period-End (Local Currency)** | Number | N | Standard element of the confirmation request — used to test for unrecorded liabilities |
| **Substantive Attention Confirmed?** | Y/N/Unknown | N | Per the ABA Statement of Policy (or local equivalent) — counsel is only expected to comment on matters given substantive attention; "Unknown" is a legitimate, common value pre-response, not a data-quality gap |
| **Bring-Down Letter Required?** | Y/N | N (system-set from Engagement Setup cutoff) | |
| Prior-Year Response Type | Enum: Full / Limited / No Comment / N/A | N | |

### 1.5 Intercompany Balance Agreement Population *(ISA 600-adjacent — not an ISA 505 external confirmation)*

| Column | Type | Required | Notes |
|---|---|---|---|
| Component A | Text | Y | |
| Component A Balance (Local Currency A) | Number | Y | As recorded on Component A's books |
| Currency A | ISO code | Y | |
| Component B | Text | Y | |
| Component B Balance (Local Currency B) | Number | Y | As recorded on Component B's books — independently sourced, never derived from Component A's figure |
| Currency B | ISO code | Y | |
| Nature of Balance | Text | Y | e.g., "Working capital loan," "Trade payable — management fee," "Cross-shipment trade balance" |
| Elimination Reference | Text | N | Consolidation elimination entry/schedule ID, if already assigned |

### 1.6 GL / Subledger Extract

| Column | Type | Required | Notes |
|---|---|---|---|
| Entity/Component Name | Text | Y | |
| Account/Customer/Matter Reference | Text | Y | Ties to population tabs |
| GL Balance as of Confirmation Date | Number | Y | |
| GL Balance as of Period-End | Number | Y (if Rollforward Required) | |
| Local Currency | ISO code | Y | |

### 1.7 Optional Inputs

- **Related-Party List** — independent source of truth for the Related Party? flag; never assume the population's self-report is complete
- **Prior-Year Confirmation Exceptions** — carried forward for trend visibility in the workpaper
- **E-Confirmation Platform Export** — raw export (Confirmation.com/Thomson Reuters format, native column names and status codes); agent normalizes to the internal tracker schema, does not require a specific platform's layout

## 2. Realistic Sample Input Excerpt (illustrative — includes intentional imperfections)

**Bank Confirmation Population (excerpt)**

| Entity | Jurisdiction | Bank | Contact Email | Account(s) | GL Balance | Ccy | Form Type | Non-Std Paragraphs | Related Party (self) | Intercompany? |
|---|---|---|---|---|---|---|---|---|---|---|
| Meridian Supply Co. | US-AICPA/ABA/BAI | First National Bank | *(blank)* | 004-88213 | 1,204,500 | USD | Expanded | LOC; Compensating Balance | N | N |
| Meridian Supply Co. | US-AICPA/ABA/BAI | Continental Trust Bank | term.confirmations@**ct-bank-secure.com** | CD-40021 | 250,000 | USD | Standard | None | N | N |
| Meridian Supply Canada Inc. | CA-CPACanada | Scotiabank | gcm.confirmations@scotiabank.com | TL-70044 | 415,000 | CAD | Expanded | Pledged Collateral; Guarantee | **N (self-reported)** | N |

*(Row 1: missing contact email — hard gate. Row 2: `ct-bank-secure.com` is a look-alike of the bank's actual `ctbank.com` domain used elsewhere in the same population — a Tier 0 domain-verification test, not a routine gap. Row 3: self-reported "N" on related party, but the Related Party List independently identifies the loan's guarantor as a director — a cross-reference test, not a data gate.)*

**Intercompany Balance Agreement (excerpt)**

| Component A | Balance A | Ccy A | Component B | Balance B | Ccy B | Nature |
|---|---|---|---|---|---|---|
| Meridian Supply Co. | 500,000 | USD | Meridian Supply Canada Inc. | 498,200 | USD-equiv | Working capital loan |
| Meridian Supply Co. | 142,000 | USD | Meridian Supply UK Ltd. | 108,500 | GBP | Trade payable — management fee |

*(Row 1: a $1,800 gap likely FX-timing or an unrecorded accrual — flagged, not resolved. Row 2: translate GBP at the cited FX rate source before comparing; a genuine ~$4,500 gap remains even after translation, consistent with a December invoice recorded by one side and not yet by the other.)*

## 3. Currency / Localization Handling

- All reconciliation performed in **local (confirmed) currency first**, including for intercompany balances — each side's own local-currency figure is validated before any cross-currency comparison.
- Where confirmation date and period-end rates differ, the workpaper shows both translated figures side by side, labeled by rate date, **with the FX Rate Source from Engagement Setup cited on the cell or its note** — an unsourced translated figure is a hard gate.
- FX-only variance (local-currency balances tie, translated figures don't) is flagged distinctly from a true balance discrepancy so reviewers aren't chasing a non-issue.

## 4. Time Horizon & Completeness Thresholds

- Chase cadence defaults: Bank/AR — 1st chase at 10 business days outstanding, 2nd at 20, escalation flag at 30. **Applies to positive confirmations only** — negative confirmations are never chased (Section 7). Legal — team-set (typically 20–40 business days given law-firm response norms).
- Completeness check at intake: population count **and $ coverage** per type must reconcile to the team-supplied expected sample and to the total FS caption balance; any gap is bridged explicitly, not silently absorbed.
- Rollforward window: if Confirmation Date < Period-End Date, the gap in days is calculated and displayed on every affected tracker row.
- **Bring-down cycle**: where Engagement Setup sets a Bring-Down Letter Cutoff, legal matters still open past that date automatically queue a second, shorter letter — this is a second dispatch cycle on the same matter, tracked as its own row, not a re-send of the original.

## 5. Missing Data Handling

| Missing field | Treatment |
|---|---|
| Contact email (any type) | Hard gate — record held in "Cannot Send" queue, never silently skipped |
| GL/subledger balance | Hard gate — cannot reconcile without it |
| Non-standard paragraph selection (bank, Expanded form) | Flagged for team clarification, never assumed "None" |
| Related Party flag (self-reported) | Always cross-checked against the Related Party List regardless of the self-reported value; a list-confirmed relationship overrides a self-reported "N" as a flag, not a silent correction |
| Estimated exposure (legal) | Permitted to be "Unable to estimate" — not a gate |
| Substantive Attention Confirmed? | "Unknown" is a legitimate pre-response value |
| Component Materiality (Engagement Setup) | Hard gate for that component's population — a group-only materiality figure is not a substitute |
| FX Rate Source | Hard gate on any translated figure — no default rate assumed |

## 6. Output Artifact & Tab Structure

Delivered as a single Excel workbook per engagement (per-component tabs nested where Group Audit = Y):

1. **Cover / Engagement Summary** — client, period-end, confirmation dates, frameworks by entity, response rate by type, overall status
2. **Bank Tracker** — one row per confirmation, jurisdiction/template used, status, dates, chase count, linked response artifact
3. **AR Tracker** — same structure, plus confirmation type; **negative-confirmation rows use the distinct status vocabulary** (Section 7), never "Outstanding"
4. **Legal Tracker** — response type classification (full/limited/no comment/none received), substantive-attention flag, unbilled-fee figures, bring-down cycle status
5. **Intercompany Matching** — both sides' balances, translated figures with FX source cited, variance, proposed likely cause (not a conclusion)
6. **Exception Schedule** — all flagged items across types, categorized by **tier** (0/1/2), standard reference, description
7. **Reconciliation Detail** — local-currency and translated figures side by side, variance, rollforward gap where applicable
8. **Unconfirmed / Alternative-Procedures Candidates** — items with no response by the reporting cutoff, explicitly flagged as needing auditor-performed alternative procedures
9. **Chase Log** — every chase email drafted (positive/legal only), date, recipient, cadence tier
10. **Changelog** — every assumption made during the run, status (Pending/Accepted/Overridden), reviewer, date

## 7. Flagging Framework — Three Tiers

**Tier 0 — Immediate Escalation (fraud/security indicators, never held for end-of-cycle reporting)**
- Response sender domain mismatched or look-alike vs. the domain the request was sent to
- Response or confirmation redirected through a client-controlled-only channel
- Response artifact showing signs of alteration inconsistent with the counterparty's known format

**Tier 1 — Structural (hard gate, blocks drafting/reconciliation for that record)**
- Missing contact email
- Missing GL/subledger balance
- Population count or $ coverage mismatch vs. expected sample/FS caption
- Currency code invalid/unrecognized
- Missing component materiality or FX rate source

**Tier 2 — Graduated (surfaced, does not block, severity-ranked)**
- Balance variance beyond the tolerance set in Engagement Setup
- Non-response past final chase cadence tier — **positive/legal only**; a negative confirmation with no reply is never in this tier
- Bank response silent on a requested non-standard paragraph
- Legal response type = Limited or No Comment, or silent on a matter not confirmed as having received substantive attention (surfaced as a classification, severity left to the team)
- Related-party balance identified via the independent list (regardless of self-reported flag)
- Intercompany balance variance beyond tolerance, net of FX-timing effects
- Response artifact indicators suggesting non-original document (fax header mismatch, no letterhead, photocopy) — distinct from the Tier 0 domain check
- Address/contact changed mid-engagement vs. prior-year population
- Near-duplicate counterparty name proposed as a match, pending team confirmation

## 8. Formatting & Audit Trail Standards

- Every tracker row carries a timestamp for each status change (sent, chased, received, reconciled) — no overwriting prior status without a visible history.
- Every drafted letter and chase email is saved as a linked file (Drive) referenced by ID from the tracker row, not pasted inline.
- Every translated (FX) figure carries its rate source as a cell comment or adjacent note — never a bare number.
- Workbook is locked to formulas for reconciliation columns (no hard-coded overrides) so a reviewer can trace every variance back to its inputs.

## 9. Presentation Standards

- Consistent color coding: Outstanding (amber), Received-Clean (green), Exception (red), Suspense/Unmatched (grey), **Negative — Delivered/No Reply (Expected)** shown in a neutral blue, distinct from amber "Outstanding" to avoid implying follow-up is owed.
- Tier 0 items rendered with a distinct, high-visibility marker separate from the standard exception color, so they are never mistaken for a routine Tier 2 item at a glance.
- Group audits: component-level tabs plus a roll-up summary tab — never a single flattened cross-entity list.
- Currency always labeled explicitly next to every figure; no unlabeled numbers.

## 10. Pre-Delivery Checklist

- [ ] Population counts **and $ coverage** per type reconcile to expected sample and to the FS caption total
- [ ] Zero records in "Cannot Send" queue, or queue explicitly accepted by team
- [ ] All Tier 1 structural flags resolved or explicitly overridden and logged
- [ ] All Tier 0 items escalated to and acknowledged by the senior/manager, with a named reviewer on file
- [ ] Reconciliation complete for every "Received" record, with FX/rollforward breakdown and rate source shown where applicable
- [ ] Intercompany matching complete for every flagged intercompany balance, with likely-cause note (not a conclusion)
- [ ] No negative-confirmation row is labeled "Outstanding" or appears in the Chase Log
- [ ] Unconfirmed/alternative-procedures list reviewed and dated
- [ ] Changelog fully populated — no blank "Pending" rows left unaddressed at delivery
- [ ] All outbound emails confirmed as drafts only, from the audit-team-controlled mailbox, zero sent by the agent

## 11. Changelog Table (template)

| # | Assumption / Flag | Tier | Record(s) Affected | Status | Reviewer | Date |
|---|---|---|---|---|---|---|
| 1 | *(e.g., "Chase cadence for legal defaulted to 25 business days — no team override supplied")* | 2 | All legal population | Pending — awaiting client confirmation | | |
