# Client Input Requirements — Audit Confirmations

As of Sep 23, 2026

## Purpose

To run external confirmations for the audit, we need one Excel workbook from you with six required tabs and up to three optional ones. This document lists every field, says whether it is required, and explains why the audit needs it.

- **One workbook per engagement.** Group audits put every component in the same workbook, identified by an Entity/Component Name column.
- **Keep the tab names and column headings exactly as shown.** If your system exports a different layout, send it as is and tell us. We will map it on our side rather than ask you to rebuild it.
- **Layout:** on each list tab, the column headings sit in row 3 (rows 1–2 are for a title and a subtitle). Engagement Setup is a two-column Field / Value list with headings in row 4, columns B–C.
- **Amounts** are in local currency with a 3-letter ISO currency code (USD, GBP, CAD, EUR) on the same row. Do not translate amounts yourself; the audit team does that.
- **Use "N/A" only where this document allows it.** Leave a field blank when the value is unknown, not "N/A" or "0".
- **Where the audit team sets a field, not you,** the field notes say so. You may be asked to confirm those values, not supply them.

## Workbook at a glance

The audit team chooses which items to confirm. You supply the contact details, balances and background for those items, plus the book balances they are compared against.

| Tab | Required? | What you provide | Why it matters |
| --- | --- | --- | --- |
| Engagement Setup | Yes | Client name, dates, entity list, frameworks (the audit team completes the rest) | Sets the dates, currencies and rules every other tab is checked against |
| Bank Confirmation Population | Yes, if bank balances are confirmed | Each bank account: bank contact, account numbers, balance, facilities | Lets us request the right bank letter for each country and ask about every facility |
| AR Confirmation Population | Yes, if receivables are confirmed | Each selected customer: contact, balance, related-party status | Lets customers confirm what they owe you |
| Legal Confirmation Population | Yes, if legal letters are sent | Each law firm and matter: exposure, assessment, unpaid fees | Lets counsel confirm litigation, claims and fees |
| Intercompany Balance Agreement | Yes, for group audits | Each intercompany balance, as booked by **both** entities | Checks both sides agree before consolidation eliminations |
| GL\_Subledger Extract | Yes | Book balance for every item above, at the confirmation date and at period-end | The figure each confirmed balance is compared with |
| Related Party List | Strongly recommended | Every related party, from an independent source | Checks the related-party flags on the other tabs |
| Prior Year Exceptions | Optional | Last year's confirmation differences | Shows repeat issues |
| E-Confirmation Platform Export | Only if a platform is used | Raw status export from Confirmation.com or similar | Tracks platform confirmations alongside emailed ones |

## 1. Engagement Setup

This tab holds the facts that apply to the whole engagement. You provide the company facts; the audit team fills in the audit parameters and may ask you to confirm them.

| Field | Required? | Supplied by | Why it's needed |
| --- | --- | --- | --- |
| Client Name | Yes | Client | Appears on every letter and links the workbook to the engagement |
| Engagement Code | Yes | Audit team | Ties this workbook to the GL extract and last year's files |
| Period-End Date | Yes | Client | The date balances are audited at; letters ask counterparties to confirm as of it |
| Confirmation Date — Bank / AR / Legal | Yes (3 dates) | Audit team, agreed with client | The "as of" date in each letter. If earlier than period-end, balances must be rolled forward |
| Rollforward Required — Bank / AR | Yes (Y/N) | Set automatically | Y whenever the confirmation date is before period-end, so the period-end book balance is also needed |
| Group Reporting Currency | Yes | Client | The currency the group consolidates in |
| Component Reporting Framework (per entity) | Yes | Client | US GAAP, IFRS or Canadian standards. Decides which auditing standard and letter wording apply, and how legal exposures are classified |
| Group Materiality | Yes | Audit team | Used to judge whether differences matter |
| Component Materiality (per entity) | Yes | Audit team | Each entity's own threshold; the group figure is not a substitute |
| Variance Tolerance — Bank / AR | Yes | Audit team | How large a difference must be before it is investigated |
| FX Rate Source & Convention | Yes | Client, agreed with audit team | e.g. "Bank of Canada daily rate, spot at confirmation date and period-end". Every translated amount must cite it |
| Chase Cadence — Bank/AR, Legal (days) | Yes | Audit team | When follow-ups are sent (default 10 and 20 business days for bank/AR) |
| Bring-Down Letter Cutoff | No | Audit team | If set, legal matters still open after this date get a short update letter near the report date |
| Engagement Partner / Manager / EQCR | Partner and Manager required | Audit team | Named sign-off and escalation contacts |
| Group Audit? | Yes (Y/N) | Audit team | If Y, the workbook is expected to cover several entities |
| Data Protection Note | No | Client | Tells us about UK GDPR or other rules on sending counterparty data across borders |

## 2. Bank Confirmation Population

List one row per bank relationship, including accounts with a zero or overdrawn balance, and facilities with no cash balance.

| Field | Required? | Why it's needed |
| --- | --- | --- |
| Entity/Component Name | Yes | Which group entity holds the account; must match Engagement Setup |
| Jurisdiction / Template Standard | Yes | US, UK or Canada (or Other). Each country uses a different standard bank letter, so there is no generic letter |
| Bank Name | Yes | Addressee of the letter |
| Bank Contact Email | Yes | Where the request goes. Must be the bank's confirmation desk or relationship manager, at the bank's own domain. Replies are checked against this domain to detect spoofed responses |
| Account Number(s) | Yes | Tells the bank which accounts to confirm. Separate several with semicolons |
| GL Balance (Local Currency) | Yes | The balance you expect the bank to confirm. May be negative, e.g. an overdraft or derivative liability |
| Local Currency | Yes | 3-letter ISO code for the balance |
| Confirmation Form Type | Yes | Standard (balances only) or Expanded (also asks about loans, guarantees and other arrangements) |
| Non-Standard Paragraphs Requested | Yes, if Expanded | Which extra items to ask about: Compensating Balance, Line of Credit, Guarantee, Derivative, Pledged Collateral, Contingent Liability, or None. A blank on an Expanded form is queried, never treated as None |
| Prior-Year Exception? | No | Y if last year's confirmation for this bank showed a difference |
| Related Party? | No | Your own flag; it is checked against the Related Party List |
| Intercompany? | No | Y if the counterparty is another group entity; the balance should then also appear on the Intercompany tab |

## 3. AR Confirmation Population

List one row per customer the audit team has selected. Use each customer's accounts-payable contact, not your own sales contact.

| Field | Required? | Why it's needed |
| --- | --- | --- |
| Entity/Component Name | Yes | Which group entity the receivable sits in |
| Customer Name | Yes | Addressee. Use the legal name; similar names across rows are queried, never merged |
| Customer Contact Email | Yes | Where the request goes. Must be an address at the customer's own domain, not a personal or intermediary address |
| GL/Subledger Balance (Local Currency) | Yes | The balance the customer is asked to agree |
| Local Currency | Yes | 3-letter ISO code |
| Confirmation Type | Yes (audit team sets) | Positive-Standard (customer confirms a stated balance), Positive-Blank (customer states the balance), or Negative (customer replies only if they disagree) |
| Threshold Rule Applied | Yes (audit team sets) | The selection rule that picked this customer. Balances outside the rule's range are queried |
| Related Party? | No | Your own flag; checked against the Related Party List |
| Prior-Year Exception? | No | Y if last year's confirmation showed a difference |
| Intercompany? | No | Y if the customer is another group entity |

Negative confirmations are never chased. No reply is the expected result, so there is no need to follow up those customers yourself.

## 4. Legal Confirmation Population

List one row per matter per law firm, including law firms kept on retainer with no active matter. Management's assessment of each matter comes from you. Counsel is asked to confirm or comment on it.

| Field | Required? | Why it's needed |
| --- | --- | --- |
| Entity/Component Name | Yes | Which group entity the matter relates to |
| Law Firm Name | Yes | Addressee of the letter |
| Law Firm Contact Email | Yes | The responsible partner or the firm's audit-response address |
| Matter Description | Yes | What counsel is asked about. Include case name or number where there is one |
| Asserted / Unasserted / N/A | Yes | Asserted = claim made against you; Unasserted = possible claim not yet made; N/A = retainer only, no active matter |
| Estimated Exposure (Local Currency) | No | Your estimate of the possible loss, or "Unable to estimate" |
| Local Currency | No | 3-letter ISO code for the exposure and fees |
| Management's Assessment | Yes | US GAAP entities: Probable / Reasonably Possible / Remote. IFRS entities: Probable / Possible / Remote. The wording must match the entity's framework in Engagement Setup |
| Unbilled/Unpaid Fees at Period-End (Local Currency) | No | Legal fees owed but not yet billed or paid. Used to check for unrecorded liabilities |
| Substantive Attention Confirmed? | No | Y / N / Unknown. Whether counsel has actively worked on the matter; Unknown is acceptable before the reply |
| Bring-Down Letter Required? | No (set automatically) | Set from the cutoff date in Engagement Setup |
| Prior-Year Response Type | No | Full / Limited / No Comment / N/A. How this firm answered last year |

## 5. Intercompany Balance Agreement

For group audits, list one row per intercompany balance, with the amount each entity records in its own books. Each side's balance must come from that entity's own ledger. Never derive one side from the other, or a real difference is hidden.

| Field | Required? | Why it's needed |
| --- | --- | --- |
| Component A | Yes | The first entity in the pair |
| Component A Balance (Local Currency A) | Yes | The balance as booked by Component A |
| Currency A | Yes | 3-letter ISO code for A's balance |
| Component B | Yes | The counterparty entity |
| Component B Balance (Local Currency B) | Yes | The balance as booked by Component B, taken from B's own ledger |
| Currency B | Yes | 3-letter ISO code for B's balance |
| Nature of Balance | Yes | e.g. working-capital loan, management fee payable, trade balance. Helps explain differences |
| Elimination Reference | No | Your consolidation elimination entry or schedule ID, if already assigned |

## 6. GL\_Subledger Extract

Provide one row per bank account, customer and legal matter listed on the tabs above, straight from your general ledger or subledger. Confirmed balances are compared with these figures.

| Field | Required? | Why it's needed |
| --- | --- | --- |
| Entity/Component Name | Yes | Which entity's ledger the balance comes from |
| Account/Customer/Matter Reference | Yes | Links the row to the matching item on another tab. Use the same account number, customer name or matter description |
| GL Balance as of Confirmation Date | Yes | Compared directly with what the counterparty confirms |
| GL Balance as of Period-End | Yes, if rollforward required | Needed when the confirmation date is before period-end, to bridge the confirmed balance to the year-end figure |
| Local Currency | Yes | 3-letter ISO code |

Provide both balance columns whenever the confirmation and period-end dates differ. With only one column, a normal movement between the two dates looks like a difference.

## 7. Optional tabs

| Tab | What to include | Why it's needed |
| --- | --- | --- |
| Related Party List | Every related party (name, relationship, entity), from a source independent of the population tabs, such as the board register or disclosure schedule | Related-party flags on the other tabs are often incomplete. This list is the reference they are checked against; a match raises a flag even if the population tab says N |
| Prior Year Exceptions | Last year's confirmation differences: counterparty, type, amount, resolution | Shows repeat issues with the same counterparty |
| E-Confirmation Platform Export | The raw export from Confirmation.com or a similar platform, unedited, in its native columns | Lets platform confirmations be tracked alongside emailed ones. Do not reformat it; we map it on our side |

## 8. Missing data and common problems

A missing email or balance holds up that item until you supply it. Other gaps are queried and do not hold anything up.

| Gap | Effect |
| --- | --- |
| Contact email missing | The request cannot be drafted. The item waits in a hold queue |
| GL balance missing | The confirmed balance cannot be compared. The item is held |
| Unknown or invalid currency code | The item is held until corrected |
| FX Rate Source missing | No translated amounts can be produced |
| Component materiality missing | That entity's items are held; the group figure is not used instead |
| Expanded bank form with no paragraphs selected | Queried with you; never assumed to be None |
| Legal exposure "Unable to estimate" | Accepted |
| Substantive attention "Unknown" | Accepted |

Common problems to avoid:

- **Contact emails at the wrong domain.** Personal addresses, your own staff, or look-alike domains (e.g. bankname-secure.com) are flagged as a possible fraud risk. Give the counterparty's official address.
- **"N/A" used where a value is expected.** Use it only for legal matters that are retainer-only.
- **Totals that don't tie.** Row counts and amounts on each population tab should agree with the audit team's selection and the financial statement caption.
- **Renamed tabs or columns.** Keep the names in this document, or send your native export and tell us.
- **Contact changes during the audit.** Tell the audit team directly. Don't edit the workbook after it has been sent.

Send the workbook to the audit team only, never to counterparties. The audit team sends all confirmation requests from its own mailbox and receives the replies directly. That independence is required by auditing standards.
