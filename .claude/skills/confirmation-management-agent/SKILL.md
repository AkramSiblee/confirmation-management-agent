---
name: confirmation-management-agent
description: Drafts, dispatches (draft-only), tracks, chases, and reconciles third-party audit confirmations — bank, accounts receivable, and legal — plus adjacent intercompany balance agreement, for Big 4-caliber, multi-jurisdiction group audits. Handles jurisdiction-specific templates, foreign currency, electronic confirmation platforms, non-standard bank paragraphs, negative-confirmation non-response mechanics, legal-letter response nuances, and email-based confirmation fraud indicators. Does not perform auditor judgment: sample selection rationale, sufficiency-of-evidence conclusions, and exception disposition remain with the engagement team.
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

# Confirmation Management Agent

This is the trigger/router file Claude Code loads automatically. It is kept
short on purpose — full detail lives in two reference docs so it isn't
duplicated (and doesn't bloat context) here:

- **[`../../../docs/workflow-skill.md`](../../../docs/workflow-skill.md)** — standards
  basis (ISA 505/AU-C 505/PCAOB AS 2310/ISA 600), scope, RACI, and the
  8 execution steps in full.
- **[`../../../docs/io-spec.md`](../../../docs/io-spec.md)** — column-level input
  schemas, the three-tier flagging framework, and the output workbook spec.
- **[`../../../CLAUDE.md`](../../../CLAUDE.md)** — non-negotiable design rules and
  known failure modes to check before touching a module (read this first
  when resuming work on the codebase itself).

## Quick reference

- Four confirmation/agreement types: **bank, AR, legal, intercompany**
  (intercompany is ISA 600-adjacent, not an ISA 505 external confirmation —
  don't conflate the two in code comments or output copy).
- Eight steps: intake -> templates -> dispatch -> tracking -> chase ->
  exception schedule -> reconciliation -> workpaper. Step 1 (`intake.py`)
  is implemented and tested; the rest are scaffolded — see `README.md`'s
  build-state table.
- Draft-only, always. No code path may call an email "send" API.
- Negative AR confirmations are never chased — a non-reply is the expected
  outcome, not an open item.
- A self-reported "Related Party?" flag is never trusted alone — always
  cross-check the independent Related Party List.
- Every translated (FX) figure must cite its rate source.
- A flagged item is a variance requiring investigation — never a
  conclusion ("error", "misstatement") in generated output.

Run `pytest` from the repo root before treating any step as done.
