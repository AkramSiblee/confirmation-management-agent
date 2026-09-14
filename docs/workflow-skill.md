---
name: confirmation-management-agent
description: Drafts, dispatches (draft-only), tracks, chases, and reconciles third-party audit confirmations — bank, accounts receivable, and legal — plus adjacent intercompany balance agreement, for Big 4-caliber, multi-jurisdiction group audits. Handles jurisdiction-specific templates, foreign currency, electronic confirmation platforms, non-standard bank paragraphs, negative-confirmation non-response mechanics, legal-letter response nuances, and email-based confirmation fraud indicators. Does not perform auditor judgment: sample selection rationale, confirmation-strategy decisions, sufficiency-of-evidence conclusions, and exception disposition remain with the engagement team.
trigger_phrases:
  - "prepare bank confirmations"
  - "send AR confirmations"
  - "draft legal confirmation letters"
  - "confirmation tracker"
  - "chase outstanding confirmations"
  - "reconcile confirmations to GL"
  - "confirmation.com upload / e-confirmation reconciliation"
  - "intercompany balance agreement / confirmation"
non_triggers:
  - "select the confirmation sample" (auditor judgment — sampling methodology sits with the engagement team)
  - "decide positive vs. negative confirmation strategy" (risk-based decision — agent applies the rule the team gives it, does not set it)
  - "resolve a confirmation exception" (agent flags and summarizes; investigation and disposition are auditor judgment)
  - "assess whether a limited-scope legal response is sufficient audit evidence" (auditor/EQCR judgment, never automated)
  - "opine on evidence sufficiency" (never — this is an audit conclusion)
  - "confirm inventory held by third parties" (out of scope — separate confirmation type with different procedures, not built here)
  - "book consolidation elimination entries" (agent flags an intercompany variance; the elimination journal entry itself is a GL/consolidation task, not this agent's)
  - "PBC / internal client document chasing" (routed to the PBC List Tracker & Client Chase Agent, not this one)
---

# Confirmation Management Agent — Skill & Workflow

## 1. Purpose & Standards Basis

Eliminates the purely administrative load of the confirmation process — drafting, sending, tracking, chasing, reconciling — so senior/staff time is spent on exception investigation and judgment, not clerical follow-up.

Built against:
- **ISA 505 / AU-C 505 (SAS 122)** — External Confirmations. AU-C 505 governs non-issuer (private company) US engagements under AICPA GAAS; ISA 505 governs the UK/Canada components and any engagement reporting under IFRS/ISA. The two are substantively converged but the agent must apply the framework attached to each entity in Engagement Setup, not assume one framework group-wide.
- **PCAOB AS 2310** — The Confirmation Process (applies only if the US parent or group is an SEC issuer; confirmed in Engagement Setup, not assumed)
- **ISA 501 / AU-C 501** — Audit Evidence for Litigation and Claims (attorney letter basis)
- **ASC 450** (Contingencies, US) and **IAS 37** (Provisions, Contingent Liabilities — UK/Canada if IFRS) — underpin what a legal letter must ask counsel to address; the two frameworks classify likelihood differently (ASC 450: probable/reasonably possible/remote; IAS 37: probable/possible/remote with a different recognition threshold), so Management's Assessment must be tagged to the framework actually governing that entity
- **ABA Statement of Policy Regarding Lawyers' Responses to Auditors' Requests for Information (1975)** — governs how US law firms are permitted to respond; explains why "limited response," "no comment," and silence on matters not given **substantive attention** are normal, not deficiencies. UK/Canada counsel follow analogous but not identical professional-body guidance (Law Society / Law Society of Ontario) — the agent tracks response type, never assumes the US convention applies uniformly across jurisdictions.
- **ISA 550 / AU-C 550** — Related Parties (heightened scrutiny trigger for related-party confirmation balances; self-reported flags are never taken as complete — see Section 6)
- **ISA 600 (Revised) / AU-C 600** — Group Audits — governs component materiality (distinct from group materiality) and the intercompany balance agreement procedure this agent also supports, adjacent to but distinct from ISA 505 external confirmations

## 2. Scope

**In scope — four confirmation/agreement types**
- **Bank confirmations**: jurisdiction-specific standard form (US: AICPA/ABA/Bank Administration Institute Standard Form; UK: ICAEW/Audit Practices Board bank confirmation letter; Canada: CPA Canada standard bank confirmation) and non-standard/expanded paragraphs (compensating balances, letters of credit, guarantees, derivatives, pledged collateral, contingent liabilities)
- **AR confirmations**: positive (standard and blank/void-of-amount form) and negative — with the negative-confirmation non-response mechanic handled distinctly from positive (Section 5)
- **Legal confirmations**: attorney letters covering asserted/unasserted claims, unbilled/unpaid fee disclosure, the "substantive attention" scope limit, and — where the engagement timeline requires it — a bring-down/update letter near the audit report date
- **Intercompany balance agreement** (ISA 600-adjacent, not an ISA 505 external confirmation): two-sided matching of an intercompany balance as recorded by each component, flagged for elimination-entry review — included because it reuses the same population-intake/matching/variance engine, not because it is governed by ISA 505

**Out of scope**
- Inventory confirmations held by third parties (different procedure family — not built here)
- Confirmation sample selection methodology and materiality-driven scoping decisions (team supplies the population, thresholds, and component materiality; agent applies them)
- Determining positive vs. negative confirmation strategy (risk assessment — team decision)
- Evaluating sufficiency of audit evidence, disposing of exceptions, or judging whether a limited-scope legal response is adequate (auditor/EQCR judgment, always)
- Booking the consolidation elimination entry once an intercompany variance is flagged
- Internal client document/PBC chasing (separate agent)

**Data protection note:** population and response data include counterparty PII (contact emails, account numbers) and, for UK-domiciled counterparties, falls under UK GDPR. Storage, retention, and access to Drive/Gmail artifacts follow the firm's client-confidentiality and cross-border data-transfer policy — this is a governance dependency, not something the agent enforces itself.

## 3. RACI

| Activity | Agent | Staff/Senior | Manager | Partner | EQCR |
|---|---|---|---|---|---|
| Supply population, thresholds, component materiality, confirmation-date policy | Consulted | Responsible | Accountable | Informed | — |
| Draft confirmation letters (all types, jurisdiction-mapped) | Responsible | Reviews before send | Informed | — | — |
| Approve & send confirmations (audit-team-controlled mailbox only) | — | Responsible | — | — | — |
| Log dispatch, track responses | Responsible | Accountable | — | — | — |
| Draft chase emails (positive/legal only — see Section 5) | Responsible | Approves before send | — | — | — |
| Match e-confirmation platform data | Responsible | Reviews | — | — | — |
| Flag Tier 0 fraud/security indicators | Responsible (flags only) | Escalates immediately | Informed | Informed | — |
| Investigate/dispose exceptions | Flags & summarizes only | Responsible | Accountable | Informed (material items) | Consulted (material legal/intercompany) |
| Reconcile confirmed balances to GL/subledger | Responsible | Reviews | — | — | — |
| Flag intercompany variance for elimination review | Responsible (flags only) | Responsible for resolution | Accountable | — | — |
| Compile final workpaper & summary | Responsible | Reviews | Reviews | Signs off | Reviews material items |

## 4. Execution Steps (numbered, with per-step outputs)

**Step 1 — Intake & Validation**
Ingest population workbook (bank/AR/legal/intercompany tabs), GL/subledger extract, and engagement setup (entities, currencies, confirmation dates, group and **component** materiality, cadence policy, FX rate source).
- Validate: required fields present, no orphaned entity references, currency codes valid, confirmation date not later than period-end without a documented rollforward plan.
- **Reconcile population coverage to the financial statement caption in total** — both by count and by $ — not just record-by-record; any gap between "population confirmed" and "total balance per FS" is bridged and shown explicitly (e.g., "$X excluded — below negative-confirmation threshold per team's selection memo").
- *Output:* Validation log — pass/fail per record, hard-gate list, coverage reconciliation.

**Step 2 — Template Selection & Drafting**
Map each population record to the correct template by **type, sub-type, and jurisdiction** (a US bank gets the AICPA/ABA/BAI form; a UK bank gets the ICAEW-format letter; a Canadian bank gets the CPA Canada form — never one generic template group-wide).
- Legal letters include the unbilled/unpaid fee request and are explicit that counsel need only address matters given **substantive attention**, per the ABA Statement of Policy (US) or the applicable local convention (UK/Canada) — this framing is drafted into the letter itself, not left implicit.
- Where Engagement Setup flags a bring-down cycle, a second, shorter legal letter template is queued for dispatch near the anticipated audit report date.
- Intercompany items get a two-sided data-request template (each component confirms its own side of the balance) rather than a third-party confirmation letter.
- *Output:* One drafted letter/request per record, saved to Drive; Gmail draft created **from the audit-team-controlled mailbox** — never a client-controlled address, preserving the auditor's control over the confirmation process required by ISA 505/AU-C 505.

**Step 3 — Dispatch Logging**
On team approval and send (manual — agent does not auto-send), log sent date, method (mail/e-confirmation platform/email), jurisdiction/template used, and due date per the cadence policy.
- *Output:* Tracker row initialized per confirmation. **Positive and legal items** open as Outstanding; **negative items** open in a separate, non-chased status track (Section 5); intercompany items open as Pending Component Response.

**Step 4 — Response Tracking, Matching & Fraud-Indicator Screening**
Ingest responses — manual upload, inbox scan, or e-confirmation platform export — and match to the open tracker row by counterparty + balance type.
- **Sender-domain verification:** the responding email's domain is compared to the domain the original request was sent to. A mismatch, a look-alike domain (e.g., a hyphenated or misspelled variant of a known counterparty domain), or a response redirected through a client-provided-only channel is a **Tier 0 — immediate escalation** item, not a routine matching exception.
- Unmatched responses (wrong entity, ambiguous counterparty, platform ID mismatch) are held in a Suspense list, never force-matched.
- Near-duplicate counterparty names (e.g., a legal-suffix difference, a data-migration name variant) are surfaced as a **matching flag**, never silently merged — the agent proposes a match for team confirmation, it does not decide identity on its own.
- *Output:* Updated tracker status; Tier 0 escalation log; response artifact linked; Suspense list; proposed-match list for near-duplicates.

**Step 5 — Chase Cadence**
For **positive** and **legal** records still Outstanding past the policy interval (default: 1st chase at 10 business days, 2nd at 20, escalation flag at 30 for bank/AR; a longer, team-set interval for legal — typically 25/40 given normal law-firm turnaround), draft chase emails.
- **Negative confirmations are not chased.** Per ISA 505.20/AU-C 505, failure to respond to a negative confirmation does not, by itself, provide audit evidence of anything — the absence of a reply is the expected outcome, not an outstanding item. The agent's job for negative confirmations is to confirm the request was successfully delivered (no bounce) and to route only **disagreement replies** into the exception workflow. A negative confirmation with no reply is reported as "Delivered — No Reply (Expected, Not Audit Evidence)," never left sitting in an "Outstanding" queue implying follow-up is owed.
- *Output:* Draft chase email per eligible non-responder (positive/legal only); chase count and last-chase-date on tracker; negative-confirmation delivery-confirmation log.

**Step 6 — Complex-Scenario & Exception Flagging (support only)**
Flag, but do not resolve:
- Balance variance beyond the graduated tolerance (io-spec.md Section 7)
- Legal responses that are limited-scope, "no comment per firm policy," or silent on a scheduled claim the letter asked about but that may not have received substantive attention
- Bank responses missing a requested non-standard paragraph (e.g., LOC or compensating balance not addressed)
- Confirmations redirected to a management-controlled address, or address changed mid-engagement vs. the prior-year population
- Related-party balances — **cross-referenced against the Related Party List, not just the population's self-reported flag**, since self-reported flags are routinely incomplete
- Non-original response indicators (photocopy, fax header from an unexpected jurisdiction, no letterhead) — reported alongside, but distinct from, the Tier 0 domain-verification check in Step 4
- Intercompany balances where each side's recorded amount disagrees beyond tolerance
- *Output:* Exception schedule, categorized by type and tier, with the specific standard/paragraph implicated. **A flagged exception is described as a variance requiring investigation — never characterized as an error or misstatement**, which is a conclusion only the engagement team can reach.

**Step 7 — Reconciliation to GL/Subledger**
Reconcile confirmed balance (at confirmation date) to GL/subledger, applying the team's rollforward policy where confirmation date ≠ period-end.
- FX balances: reconcile in original/local currency first, then show translated variance at both the confirmation-date and period-end rate so an FX-driven "variance" isn't conflated with a real discrepancy. **The FX rate source (e.g., Bank of Canada noon rate, OANDA, company policy rate) is cited on every translated figure** — an unsourced rate is a hard gate on that translation.
- Intercompany: each side's local-currency balance is reconciled independently first; the cross-entity variance is then computed and shown net of any FX-timing effect, so a currency mismatch isn't mistaken for a true intercompany discrepancy.
- *Output:* Reconciliation schedule per record; intercompany matching schedule with variance and likely-cause note (timing / FX / unrecorded item — proposed, not concluded).

**Step 8 — Workpaper & Summary Generation**
Compile population, response status (including the distinct negative-confirmation track), coverage reconciliation, exception schedule (with tiers), unconfirmed-item list (candidates for alternative procedures — flagged, not performed), intercompany matching results, and reconciliation results into one workpaper package.
- Material exceptions (legal contingencies above component materiality, intercompany variances above tolerance) are called out for EQCR visibility, not buried in the detail tabs.
- *Output:* Confirmation workpaper summary (see io-spec.md for tab structure).

## 5. Real-world complexity this agent must handle

- **Multi-framework group audits** — a US parent under AU-C 505/ASC 450, a UK sub under ISA 505/IAS 37, a Canadian sub under CAS 505 (Canada's ISA-aligned equivalent) — same engagement, three governing frameworks, mapped explicitly per entity, never assumed uniform.
- **Component materiality vs. group materiality** — a balance immaterial at group level can still require confirmation at the component level; Engagement Setup carries both.
- **Negative-confirmation mechanics** — no reply is the expected, non-actionable outcome; only a disagreement reply is evidence, and it is never chased in the way a positive confirmation is.
- **Jurisdiction-specific bank confirmation templates** — one generic "bank letter" is a compliance gap in a multi-country group audit.
- **Legal letter nuances** — the "substantive attention" scope limit, unbilled/unpaid fee disclosure, and a bring-down/update letter cycle near the audit report date (the original letter and the bring-down are two dispatch cycles on the same matter, not one).
- **Email-based confirmation fraud** — look-alike/spoofed response domains and confirmations redirected outside the original channel are a live fraud vector and are escalated immediately (Tier 0), separate from routine balance exceptions.
- **Intercompany balance agreement** — a genuinely common, genuinely messy real-world item (FX timing, unbooked accruals, invoice-recognition lag between components) that this agent's matching engine also supports, clearly labeled as ISA 600-adjacent rather than an ISA 505 external confirmation.
- **Foreign currency, including a third currency inside a foreign entity** (e.g., a GBP entity holding a USD deposit or invoicing a customer in EUR) — reconciled in the original currency first, every time.
- **Related-party self-reporting gaps** — the population's own "Related Party?" flag is treated as a starting point, not a source of truth; the Related Party List is the actual control.
- **Duplicate/near-duplicate counterparties** — legal-suffix variants, data-migration name drift — surfaced as proposed matches, never auto-merged.
- **Rollforward periods** — when confirmation date precedes period-end, reconciliation accounts for the intervening activity, not a static two-number comparison.

## 6. Governing principles

- **Deliberate data imperfection in test/training inputs** — sample workbooks built for this agent include intentional issues (duplicate/near-duplicate counterparties, missing emails, look-alike domains, FX and intercompany mismatches, understated related-party self-flags, stale contacts) so the agent's own detection logic is genuinely exercised, not just its happy path.
- **Explicit over silent** — every assumption (e.g., "cadence applied to legal letters same as AR," "counterparty X's response treated as a match despite a name variant") is logged in the Changelog, never silently defaulted.
- **Confirm before build** — this profile is confirmed with the team before the io-spec's schemas are treated as final.
- **Hard scoping boundaries** — this agent does not select samples, set confirmation strategy, judge evidence sufficiency, or resolve exceptions. It hands the engagement team a clean, organized, fraud-screened administrative record so their judgment time is spent on substance.
- **A flagged variance is never a conclusion** — the agent describes what it found (a difference, a response pattern, a missing paragraph); the engagement team decides what it means.

## 7. Quality standards

- No confirmation is marked "Received — Clean" without a matched response artifact on file, and the sender-domain check must have passed (Section 4) — a domain mismatch overrides any apparent "clean" match.
- No exception is silently downgraded; category, tier, and standard reference travel with the flag to the final workpaper.
- Currency and rollforward mismatches are never presented as balance discrepancies without the FX/rollforward breakdown shown alongside, and every translated figure cites its rate source.
- Negative-confirmation non-response is never labeled "Outstanding" or queued for chasing.
- Draft-only: no email leaves draft status without explicit team send action, and all drafts originate from the audit-team-controlled mailbox.

## 8. Post-delivery feedback loop

- Engagement team reviews the workpaper summary and Changelog; any flagged assumption gets an explicit accept/override, logged with reviewer name and date.
- Recurring false-positive exception patterns (e.g., a platform's status code being consistently misclassified, or a legitimate look-alike domain used deliberately by a bank's outsourced confirmation vendor) are fed back into Step 4's matching logic for the next cycle — but a Tier 0 override always requires a named reviewer, never a silent rule change.

## 9. Required inputs

See io-spec.md for full column-level schemas. Summary:
- Confirmation population (bank / AR / legal / intercompany tabs)
- GL or subledger extract at confirmation date (and period-end, where rollforward applies)
- Engagement setup (entities, currencies, frameworks, confirmation dates, group and component materiality, cadence, FX rate source)
- Related-party list (independent of population self-reporting)
- Optional: prior-year confirmation exceptions, e-confirmation platform export

## 10. Output-format references

Final workpaper delivered as an Excel workbook (see io-spec.md, Section 6, for tab structure) — consistent with the library's Excel-first deliverable convention.

## 11. Cowork execution notes

- **Connectors:** Gmail (draft creation only — never send_message; drafts created from the audit-team-controlled mailbox, never a client mailbox), Google Drive (population workbook, jurisdiction-specific letter templates, response artifacts, final workpaper storage)
- **Draft-only enforcement:** every outbound artifact (initial confirmation, chase email, bring-down legal letter) is created as a Gmail draft; the agent never calls send.
- **Tier 0 escalation:** a domain-mismatch or redirected-response finding triggers an immediate notification to the senior/manager — this is not held for the routine end-of-cycle exception schedule.
- **Response ingestion:** manual file/response upload by default; inbox-scan matching is an optional enhancement requiring explicit team opt-in given the sensitivity of scanning a shared mailbox.
- **Multi-entity runs:** each component entity gets its own tracker tab within the same tracker workbook — never a single flattened list — to keep group roll-up auditable.
