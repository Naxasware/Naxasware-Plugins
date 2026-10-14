> Chain: stage=2 | skill=ai-system-architect | upstream=01-requirements.md | next=ai-workflow-architect

# Architecture: Supplier Invoice Intake and Approval Automation (chain example)

- **Schema version:** 1.1
- **Mode:** requirements_to_architecture

## Business Context

- **Summary:** AP clerks re-key emailed supplier invoices into an ERP by hand; duplicates have been paid. Goal: read, match, route and post invoices with a person approving every payment unless the business decides otherwise (CONFLICT-001).

### Evidence ids

- EV-001
- EV-002

## Architecture Drivers

| Id | Statement | Requirement ids | Label |
|---|---|---|---|
| AD-001 | No payment without a recorded human approval; the AI never approves or pays (locked). | BR-001, BR-002, FR-006 |  |
| AD-002 | A supplier and invoice number may be posted once; the client has paid a duplicate before. | BR-003, FR-004, FR-007 |  |
| AD-003 | Invoice volume is unknown, so nothing may be sized or split for scale yet. | NFR-002 | Unknown |
| AD-004 | ERP vendor and API capabilities are unknown; the integration must be isolated behind one adapter. | IR-002, CON-001, DEP-001 | Unknown |
| AD-005 | Every state change must be reconstructable for audit. | FR-009, NFR-004, BO-003 |  |
| AD-006 | Invoice files and their text are untrusted input that an AI step will read. | AIR-001, NFR-001 |  |

## Constraints

| Id | Statement | Cites |
|---|---|---|
| CST-001 | The existing ERP stays; integrate through its REST API. | CON-001 |

## Quality Attributes

| Id | Name | Status | Note |
|---|---|---|---|
| QA-001 | Payment control (no unapproved payment) | Covered | ADR-002 enforces it at the ERP gateway, not only in the UI. |
| QA-002 | Security | Partially Covered | Design controls exist; NFR-001 has no measurable target. |
| QA-003 | Auditability | Partially Covered | ADR-005 records events; retention period UNKNOWN. |
| QA-004 | Speed | Unknown | NFR-002 target not defined; volume unknown. |
| QA-005 | Extraction accuracy | Unknown | NFR-003 target not defined; needs a labelled sample set. |
| QA-006 | Availability and recovery | Unknown | No requirement stated; not designed. |

## Architecture Options

| Id | Name | Trade off |
|---|---|---|
| OPT-A | Modular monolith with database-backed job queue | Fewest moving parts and one thing to run; scaling parts independently is harder later. Fits unknown, probably modest volume. |
| OPT-B | Buy or configure an invoice-automation or RPA product | Fastest start if a product fits the ERP; locks the approval rules and AI behavior to the vendor; fit REQUIRES VALIDATION (vendor unknown). |
| OPT-C | Event-driven services with a message broker | Independent scaling and isolation; heavy for an unknown, likely small load and a team of unknown size. No requirement calls for it. |

## Selected Architecture

- **Style:** Modular monolith (OPT-A)
- **Rationale:** Requirements show no need for independent scaling (AD-003) and one hard control point (AD-001). Would change if: volume proves high, or the ERP API cannot post safely, or a product (OPT-B) covers BR-001 and FR-004 natively.
- **Classification:** RECOMMENDED
- **Confidence:** Medium

## Components

| Id | Name | Origin | Responsibility | Classification | Evidence ids |
|---|---|---|---|---|---|
| COMP-001 | Shared Mailbox | stated | Existing AP mailbox that receives supplier invoices (provider UNKNOWN). | RECOMMENDED | EV-001 |
| COMP-002 | Mailbox Connector | recommended | Fetches new emails, stores each PDF once (FR-001); safe against repeat delivery. | RECOMMENDED |  |
| COMP-003 | Invoice Registry | recommended | Holds invoice state machine, duplicate check (FR-004, BR-003), and the posting key. | RECOMMENDED |  |
| COMP-004 | Extraction Service | recommended | Only AI component: turns a PDF into schema-checked fields with confidence (FR-002, AIR-001). No tools, no ERP access. | RECOMMENDED |  |
| COMP-005 | Matching Service | recommended | Deterministic PO match and arithmetic checks (FR-003). | RECOMMENDED |  |
| COMP-006 | Approval Service | recommended | Routes by amount (FR-005), records human decisions (FR-006), reminders and escalation (FR-010). | RECOMMENDED |  |
| COMP-007 | Review UI | recommended | Exception queue for clerks (FR-008), approval screen showing the original PDF beside extracted values, status report (FR-011). | RECOMMENDED |  |
| COMP-008 | ERP Gateway | recommended | Only path to the ERP; refuses to post without a recorded approval (ADR-002); idempotent posting (ADR-004). | RECOMMENDED |  |
| COMP-009 | ERP System | stated | Existing ERP with a REST API (vendor UNKNOWN). | RECOMMENDED | EV-001 |
| COMP-010 | Audit Log | recommended | Append-only event record (FR-009). | RECOMMENDED |  |
| COMP-011 | Notification Sender | recommended | Email to approvers and clerks (A-003). | RECOMMENDED |  |
| COMP-012 | Invoice Database | recommended | Relational store for invoices, approvals and queue state. Engine not chosen. | RECOMMENDED |  |
| COMP-013 | Document Store | recommended | Keeps original PDFs unchanged for audit and reviewer comparison. | RECOMMENDED |  |

## Data Architecture

- **Store:** Relational database for state and approvals; separate document store for original PDFs
- **Note:** Engine, retention and region are UNKNOWN (retention: Q-008). Supplier and PO data stay in the ERP (A-005); the system keeps references, not copies.

## API Architecture

- **Inbound:** Review UI to application over authenticated HTTPS; no public API requirement exists.
- **Outbound:** ERP REST API through COMP-008 only. Needed capabilities (read PO and receipt, create payable, detect a repeat post) REQUIRES VALIDATION (Q-004).

## Integration Architecture


### Interfaces

| Id | Name | Status | Note | Workflow risk |
|---|---|---|---|---|
| INT-001 | Mailbox to Mailbox Connector | REQUIRES VALIDATION | Provider and access method UNKNOWN (IR-001). |  |
| INT-002 | ERP Gateway to ERP System | REQUIRES VALIDATION |  | If the ERP cannot reject a repeat post, duplicate payables depend on our own posting key alone (RISK-002). |

## Security Architecture

- **Authentication:** Staff sign in through the company identity provider (provider UNKNOWN).
- **Authorization:** Roles AP Clerk, AP Manager, Controller. Clerk cannot approve. Whether the person who corrected data may also approve is OPTIONAL and open (Q-009).
- **Secrets:** Mailbox and ERP credentials stored in a secret manager; no values in code or documents.
- **Ai boundary:** Invoice text is data, never instructions. Extraction output is accepted only if it matches a fixed schema.
- **Files:** Scan attachments before processing (RECOMMENDED); accept PDF types only.

## Infrastructure

- **Runtime:** UNKNOWN (host, cloud and team skills not provided)
- **Note:** No sizing given because volume is unknown (Q-001).

## Observability

- **Approach:** Correlation id per invoice across all modules; alert on invoices stuck in a state past a limit and on ERP post failures. Alert limits NOT PROVIDED.

## AI Architecture

- **Use:** Field extraction only (AIR-001).
- **Model strategy:** Hosted or local model class UNKNOWN; model choice is time-sensitive and deliberately not fixed here. Supplier data handling by any hosted provider REQUIRES VALIDATION (RISK-006).
- **Controls:** Deterministic checks after extraction (line sum equals total, date valid, currency known); low-confidence or failed checks go to the exception queue; AI has no tool, ERP or approval access.
- **Evaluation:** Measure against a labelled sample of real invoices once Q-005 sets targets.

## Decisions

| Id | Title | Classification | Driver | Components | Confidence | Options considered | Consequences |
|---|---|---|---|---|---|---|---|
| ADR-001 | Build one modular monolith with a database-backed job queue | RECOMMENDED | AD-003 | COMP-002, COMP-003, COMP-005, COMP-006 | Medium | OPT-A, OPT-B, OPT-C | Easy to run; revisit if volume or team structure changes. |
| ADR-002 | Enforce human approval at the ERP Gateway, not only in the UI | REQUIRED | AD-001 | COMP-006, COMP-008 | High |  | A defect in the UI cannot cause an unapproved payment; the gateway checks for a stored human decision before every post. |
| ADR-003 | Limit AI to extraction behind a schema check, with no tools | REQUIRED | AD-006 | COMP-004 | High |  | Prompt injection can at worst produce wrong fields, which checks and humans catch. |
| ADR-004 | Post to the ERP with our own idempotency key and a prior lookup | REQUIRED | AD-002 | COMP-008, COMP-003 | Medium |  | Needs ERP lookup capability; REQUIRES VALIDATION (Q-004). |
| ADR-005 | Record every state change in an append-only audit log | REQUIRED | AD-005 | COMP-010 | High |  |  |
| ADR-006 | Make the small-invoice policy a setting, default to human approval for all | RECOMMENDED | AD-001 | COMP-006 | Medium |  | Does not decide CONFLICT-001. The safe default follows locked BR-001 until the business answers Q-003. |

## Risk Register

| Id | Risk | Evidence | Impact | Likelihood | Mitigation | Contingency | Affected component |
|---|---|---|---|---|---|---|---|
| RISK-001 | Prompt injection: text inside an invoice tries to steer the AI | ASSUMED (typical for document-reading AI; no incident reported) | High | Medium | ADR-003: schema-only output, no tools, deterministic checks | Quarantine the invoice and review manually | COMP-004 |
| RISK-002 | Duplicate payable created if the ERP cannot detect a repeat post | ASSUMED; ERP capability UNKNOWN (Q-004) | High | Medium | ADR-004 key plus lookup; reconcile daily against the ERP | Void the duplicate in the ERP by a person | COMP-008 |
| RISK-003 | Small invoices paid with no human if BR-004 is adopted without safeguards | USER_STATED conflict (CONFLICT-001) | High | Medium | ADR-006 default to approval; require business owner sign-off for any exception | Switch the setting back to approve-all | COMP-006 |
| RISK-004 | Approvals stall and invoices age | ASSUMED; no wait limit given (Q-006) | Medium | High | Reminders and escalation (FR-010) with limits once defined | Manager reassigns manually | COMP-006 |
| RISK-005 | A human approves a wrong amount that the AI misread | INFERRED | High | Medium | Show original PDF beside extracted values; arithmetic checks | Reverse in the ERP before payment run | COMP-007 |
| RISK-006 | Supplier bank or contact data sent to an external AI provider | ASSUMED; provider UNKNOWN | Medium | Medium | Decide provider and data terms before build; mask where possible | Switch to a local model | COMP-004 |

## Assumptions

| Id | Text |
|---|---|
| A-006 | One deployable unit is acceptable to the team. Reason: team size and skills not provided. Impact if wrong: structure changes. |
| A-007 | Original PDFs must be kept unchanged for audit. Reason: FR-009 asks for a full trail. Impact if wrong: less storage. |

## Open Questions

| Id | Text | Why |
|---|---|---|
| Q-007 | Which company identity provider and hosting platform are in use? | Authentication and runtime choices. |
| Q-008 | How long must invoices and the audit log be kept, and under which rules? | Storage and deletion design. |
| Q-009 | May the person who corrected an invoice also approve it? | Separation of duties. |
| Q-010 | May invoice data go to an external AI provider? | Model strategy, RISK-006. |

## Evidence

| Id | Types | Confidence | Note | Sources |
|---|---|---|---|---|
| EV-001 | USER_STATED | High | 00-client-brief.md: mailbox, ERP with REST API, approval rules |  |
| EV-002 | DOCUMENTED | High | Requirements document | 01-requirements.md |
| EV-003 | RECOMMENDED | Medium | Design proposals in this document |  |

## Carried forward from upstream

- **Assumptions:** A-001, A-002, A-003, A-004, A-005 still hold; none contradicted.
- **Questions:** Q-001, Q-002, Q-003, Q-004, Q-005, Q-006 still open; Q-003 and Q-004 are blocking for the workflow stage.

## Upstream Coverage

| Upstream | Handled by | Status | Reason |
|---|---|---|---|
| FR-001 | COMP-002, ADR-001 | Covered |  |
| FR-002 | COMP-004, ADR-003 | Covered |  |
| FR-003 | COMP-005 | Covered |  |
| FR-004 | COMP-003, ADR-004 | Covered |  |
| FR-005 | COMP-006, ADR-006 | Covered |  |
| FR-006 | COMP-006, ADR-002 | Covered |  |
| FR-007 | COMP-008, ADR-004 | Covered |  |
| FR-008 | COMP-007 | Covered |  |
| FR-009 | COMP-010, ADR-005 | Covered |  |
| FR-010 | COMP-006, COMP-011 | Covered |  |
| FR-011 | COMP-007 | Covered |  |
| NFR-001 | security_architecture, ADR-003 | Covered |  |
| NFR-002 | none | Deferred | No target defined upstream (Q-005); volume unknown (Q-001) |
| NFR-003 | COMP-004 | Deferred | No target defined upstream (Q-005); evaluation approach in ai_architecture |
| NFR-004 | COMP-010, ADR-005 | Partially covered |  |
| BR-001 | ADR-002, COMP-008 | Covered |  |
| BR-002 | COMP-006, ADR-006 | Covered |  |
| BR-003 | COMP-003, ADR-004 | Covered |  |
| BR-004 | ADR-006 | Deferred | In conflict with BR-001 (CONFLICT-001, Q-003); built as a setting, default off |
| AIR-001 | COMP-004, ADR-003 | Covered |  |
| IR-001 | COMP-002, INT-001 | Covered |  |
| IR-002 | COMP-008, INT-002 | Covered |  |
| CON-001 | CST-001 | Covered |  |
| DEP-001 | INT-001, INT-002 | Covered |  |

## Traceability

| Requirement | Driver | Decision | Component |
|---|---|---|---|
| FR-001 | AD-002 | ADR-001 | COMP-002 |
| FR-002 | AD-006 | ADR-003 | COMP-004 |
| FR-003 | AD-002 | ADR-001 | COMP-005 |
| FR-004 | AD-002 | ADR-004 | COMP-003 |
| FR-005 | AD-001 | ADR-006 | COMP-006 |
| FR-006 | AD-001 | ADR-002 | COMP-006 |
| FR-007 | AD-002 | ADR-004 | COMP-008 |
| FR-008 | AD-006 | ADR-003 | COMP-007 |
| FR-009 | AD-005 | ADR-005 | COMP-010 |
| FR-010 | AD-001 | ADR-006 | COMP-011 |
| FR-011 | AD-005 | ADR-001 | COMP-007 |
| BR-001 | AD-001 | ADR-002 | COMP-008 |
| BR-003 | AD-002 | ADR-004 | COMP-003 |
| BR-002 | AD-001 | ADR-006 | COMP-006 |
| IR-001 | AD-003 | ADR-001 | COMP-002 |
| IR-002 | AD-004 | ADR-004 | COMP-008 |
| DEP-001 | AD-004 | ADR-004 | COMP-008 |

## Handoff to next stage
- Next skill: ai-workflow-architect
- Must cover: FR-001 to FR-009, BR-001, BR-003, ADR-002, ADR-004, COMP-006, COMP-008, INT-002
- Locked decisions: BR-001
- Blocking questions: Q-003, Q-004
- Next A: 008
- Next Q: 011
