> Chain: stage=1 | skill=ai-requirements-analyst | upstream=none | next=ai-system-architect

# Requirements: Supplier Invoice Intake and Approval Automation

Produced by: ai-requirements-analyst (offline mode: no repository or system access, conversation input only)
Mode: Generation (Standard). Input: 00-client-brief.md

## Problem Statement
AP clerks re-type supplier invoices from email PDFs into the ERP by hand. The client reports slowness, typing errors and one or more duplicate payments (USER_STATED). No volume, cost or error-rate figures were provided, so none are used here.

## Business Objectives
BO-001: Reduce manual re-keying of supplier invoices. Success measure: not defined (see Q-005).
BO-002: Stop duplicate and mismatched payments. Success measure: not defined (see Q-005).
BO-003: Keep a full record of who approved what and when.

## Stakeholders and Actors
ST-001: AP Manager. Interest: approval workload, control over spend.
ST-002: Controller. Interest: oversight of very large payments.
ACT-001: AP Clerk (4 people). Handles exceptions; no payment authority stated.
ACT-002: AP Manager (1 person). Approves invoices above threshold T1.
ACT-003: Controller. Approves invoices above threshold T2.
ACT-004: Supplier. Sends invoices by email; has no system access (ASSUMED, A-004).
ACT-005: ERP system. Source of purchase orders, target of posted invoices.

## Functional Requirements

FR-001 — Receive invoices from the shared mailbox
Actor: ACT-005 / system. Trigger: a new email with an attachment arrives in the AP mailbox. Priority: Must
Behavior: System collects each PDF attachment as one invoice candidate and records the source email.
Evidence: 00-client-brief.md (shared mailbox, PDF attachments)
Evidence type: USER_STATED
Confidence: High
AC-001-1: Given an email with one PDF attachment arrives, When the system polls or is notified, Then exactly one invoice candidate is created and linked to the email.
AC-001-2: Given the same email is delivered or processed twice, When intake runs, Then no second candidate is created.

FR-002 — Extract invoice data
Actor: system (AI-assisted, see AIR-001). Priority: Must
Behavior: System reads each invoice and produces supplier, invoice number, invoice date, currency, total, line items and PO reference, each with a confidence indicator.
Evidence: 00-client-brief.md ("reads the invoices"; "AI must never approve")
Evidence type: USER_STATED, INFERRED
Confidence: Medium
AC-002-1: Given a readable invoice, When extraction completes, Then every field above is populated or explicitly marked missing.
AC-002-2: Given a field below the confidence cut-off (value not defined, see Q-005), When extraction completes, Then the invoice goes to the exception queue (FR-008).

FR-003 — Match invoice to purchase order
Actor: system. Priority: Must
Behavior: System compares the invoice to the referenced purchase order and reports match or specific differences.
Evidence: 00-client-brief.md ("checks them against our purchase orders")
Evidence type: USER_STATED
Confidence: High
AC-003-1: Given an invoice whose PO exists and amounts agree, When matching runs, Then the invoice is marked matched.
AC-003-2: Given a missing PO or a difference, When matching runs, Then the invoice is marked mismatched with the reason and sent to FR-008.

FR-004 — Detect duplicate invoices
Actor: system. Priority: Must
Behavior: System flags an invoice whose supplier and invoice number were already received or posted (BR-003).
Evidence: 00-client-brief.md ("paid the same invoice twice")
Evidence type: USER_STATED
Confidence: High
AC-004-1: Given an invoice with a supplier and number already on record, When it is received, Then it is flagged duplicate and not routed for payment.

FR-005 — Route for approval by amount
Actor: system. Priority: Must
Behavior: System selects the approver by invoice total using BR-002.
Evidence: 00-client-brief.md (thresholds exist; values not given)
Evidence type: USER_STATED
Confidence: Medium
AC-005-1: Given a total above T1 and not above T2, When routing runs, Then the AP Manager is the approver.
AC-005-2: Given a total above T2, When routing runs, Then the Controller is the approver.

FR-006 — Record an approval decision
Actor: ACT-002, ACT-003. Priority: Must
Behavior: An authorized person approves or rejects; the decision, person and time are stored. Only a person can do this (BR-001).
Evidence: 00-client-brief.md ("nothing gets paid unless a person has approved")
Evidence type: USER_STATED
Confidence: High
AC-006-1: Given a pending invoice, When no authorized person has decided, Then it cannot be posted for payment.

FR-007 — Post approved invoice to the ERP
Actor: system. Priority: Must
Behavior: System creates the payable in the ERP through its REST API once approved, and stores the ERP reference.
Evidence: 00-client-brief.md ("re-type into our ERP"; "ERP has a REST API")
Evidence type: USER_STATED
Confidence: Medium
AC-007-1: Given an approved invoice, When posting runs, Then one ERP payable exists and its reference is stored.
AC-007-2: Given posting is retried after a failure, When the ERP already holds the payable, Then no second payable is created.

FR-008 — Exception queue for clerks
Actor: ACT-001. Priority: Must
Behavior: Invoices that cannot be read, matched or trusted wait in a queue where a clerk corrects data or rejects.
Evidence: derived from FR-002 and FR-003 (no explicit client statement)
Evidence type: INFERRED
Confidence: Medium
AC-008-1: Given an invoice in the queue, When a clerk corrects it, Then it re-enters matching with the correction logged.

FR-009 — Audit trail
Actor: system. Priority: Must
Behavior: Every state change, extraction result, match result, approval and ERP post is recorded with who/what and when.
Evidence: 00-client-brief.md ("full audit trail")
Evidence type: USER_STATED
Confidence: High
AC-009-1: Given any invoice, When an auditor asks, Then its complete history can be listed in time order.

FR-010 — Notify approvers and chase unanswered approvals
Actor: system. Priority: Should
Behavior: Approvers are told when work waits; unanswered requests are reminded and then escalated.
Evidence: none from client; needed because FR-006 can stall (see A-003, Q-006)
Evidence type: ASSUMED
Confidence: Low
AC-010-1: Given an approval request unanswered past the limit (value not defined, Q-006), When the limit passes, Then a reminder is sent and the escalation path starts.

FR-011 — Status and ageing report
Actor: ACT-002. Priority: Could
Behavior: AP Manager sees invoices by state and age.
Evidence: none from client
Evidence type: ASSUMED
Confidence: Low
AC-011-1: Given invoices in several states, When the report is opened, Then counts and ages per state are shown.

## Business Rules
BR-001: Nothing is paid unless a person has approved it. The AI never approves or pays. LOCKED DECISION (USER_STATED, High).
BR-002: Invoices above threshold T1 need the AP Manager; above T2 the Controller. T1 and T2 are UNKNOWN (Q-002). (USER_STATED, Medium)
BR-003: A supplier and invoice number pair is posted at most once. (INFERRED from the duplicate payment, Medium)
BR-004: Small invoices go straight through with nobody looking. (USER_STATED) STATUS: IN CONFLICT with BR-001, see CONFLICT-001. Not carried into any requirement until decided.

CONFLICT-001
Documented: BR-001 says no payment without a person's approval. BR-004 says small invoices pass without anyone looking.
Observed: both statements are in the same brief; no source says which wins.
Status: Requires business decision (Q-003). This analysis does not pick a side. A reading that satisfies both (a person approves low-value invoices in a lightweight way, such as a batch confirmation) is only a suggestion, not a requirement.

## Data Requirements
DR-001: Invoice: supplier, invoice number, date, currency, total, lines, PO reference, state, source email, ERP reference.
DR-002: Supplier: identity as known to the ERP. Source of truth: ERP (ASSUMED, A-005).
DR-003: Approval record: invoice, approver, decision, reason, time.

## Non-Functional Requirements
NFR-001: Security. Roles limit who may approve; invoice content is untrusted input; credentials are held outside the documents. "Secure" is not measurable as written. Target: not defined. (USER_STATED word, INFERRED content)
NFR-002: Speed. "Fast" is not measurable as written. Target: not defined (Q-005).
NFR-003: Accuracy. "Accurate" is not measurable as written. Target: not defined (Q-005).
NFR-004: Auditability. Records must be kept; retention period and compliance regime are UNKNOWN.

## Integrations, AI, Constraints, Dependencies
IR-001: Shared mailbox. Provider UNKNOWN. Direction: in. Failure behavior: not defined.
IR-002: ERP via REST API. Vendor UNKNOWN. Needed capabilities (read POs, read goods receipts, create payable, safe repeat posting) are REQUIRES VALIDATION.
AIR-001: AI is used only to read invoices (FR-002). Human review point: exception queue (FR-008). AI has no approval or payment role (BR-001). Accuracy expectation: not defined. Privacy: invoices may hold supplier bank details (INFERRED).
CON-001: The existing ERP stays; the system integrates with it. (USER_STATED)
DEP-001: Access to the ERP API and the mailbox. (INFERRED)

## Assumptions
A-001: Invoices arrive as PDF attachments, some possibly scanned images. Reason: brief says PDF. Impact if wrong: scanned files need image reading. Confirm: yes.
A-002: One legal entity, one currency. Reason: not stated. Impact if wrong: thresholds and matching change per entity or currency. Confirm: yes.
A-003: Approvers are notified by email. Reason: no channel stated. Impact if wrong: notification design changes. Confirm: yes.
A-004: Suppliers never log in. Reason: not mentioned. Impact if wrong: a supplier portal is a new scope. Confirm: no.
A-005: The ERP is the source of truth for suppliers and POs. Reason: invoices are matched to POs held there. Impact if wrong: a second data source is needed. Confirm: yes.

## Open Questions
Q-001: How many invoices arrive per month, and what is the busiest period? Why: sizing and cost. (Blocks: architecture)
Q-002: What are the values of T1 and T2, and in which currency? Why: routing.
Q-003: May small invoices be posted without a person's approval (BR-004), or does BR-001 apply to all? Why: it decides whether a human step exists for every invoice. (Blocks: architecture, workflow)
Q-004: Which ERP vendor and version, and does its API support reading POs and goods receipts, creating a payable, and rejecting a repeat post? Why: integration design.
Q-005: What numeric targets mean "fast" and "accurate" (time from receipt to approval request; share of invoices needing no correction), and what is the cut-off for low confidence? Why: testable quality bar.
Q-006: How long may an approval wait, who covers an absent approver? Why: waiting steps need a limit.
Also unresolved, lower impact: audit retention period, invoice languages and currencies.

## Traceability
| Objective | Functional requirements |
|---|---|
| BO-001 | FR-001, FR-002, FR-008 |
| BO-002 | FR-003, FR-004, FR-007 |
| BO-003 | FR-006, FR-009 |

## Handoff to next stage
- Next skill: ai-system-architect
- Must cover: FR-001 to FR-009, BR-001, BR-003, AIR-001, IR-002
- Locked decisions: BR-001
- Blocking questions: Q-003, Q-004
- Next A: 006
- Next Q: 007
