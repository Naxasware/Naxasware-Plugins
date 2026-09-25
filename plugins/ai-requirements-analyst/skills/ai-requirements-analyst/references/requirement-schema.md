# Requirement Schema Reference

Field-by-field structures for each artifact type. Not every field is needed for every requirement — use judgment about what actually matters for a given item, and leave out fields you have nothing to say about rather than filling them with filler.

## ID scheme

| Prefix | Meaning |
|---|---|
| BO | Business Objective |
| ST | Stakeholder |
| ACT | Actor |
| FR | Functional Requirement |
| NFR | Non-Functional Requirement |
| BR | Business Rule |
| DR | Data Requirement |
| IR | Integration Requirement |
| AIR | AI Requirement |
| AR | Automation Requirement |
| UC | Use Case |
| US | User Story |
| AC | Acceptance Criterion |
| A | Assumption |
| Q | Open Question |
| CON | Constraint |
| DEP | Dependency |

IDs are sequential and stable within a document (FR-001, FR-002, ...) and, once assigned, shouldn't be renumbered on revision — if FR-003 is removed later, leave a gap rather than reflow every ID after it, so old references (in a traceability matrix, in a conversation, in a ticket) stay valid.

## Stakeholder (ST-xxx)

Stakeholder / Role / Interest / Responsibilities / Needs / Permissions / Expected interaction

Distinguish a **stakeholder** (has an interest in the outcome — may never touch the system) from a **system actor** (actually interacts with the system). The same person can be both; the two lists don't have to match.

## Actor (ACT-xxx)

For each actor: what they can see, create, edit, delete, approve, export, and what notifications they receive.

## Functional Requirement (FR-xxx)

ID / Name / Description / Actor / Trigger / Preconditions / Main behavior / Alternative behavior / Business rules / Output / Dependencies / Acceptance criteria / Priority

Example:

```
FR-001 — Create Vehicle
Actor: Fleet Administrator
Trigger: Administrator selects "Add Vehicle"
Precondition: Administrator is authenticated.
Behavior: System allows the administrator to enter vehicle information.
Required data: Registration number, Make, Model, Year, Current mileage, Assigned department
Acceptance: A valid vehicle record is created and receives a unique identifier.
```

## User Story (US-xxx)

`As a [role], I want [capability], so that [business value].`

Use these to communicate intent quickly, not as a replacement for a detailed FR when the implementation detail actually matters — a story without the underlying FR/AC often isn't enough for a developer to build from.

## Use Case (UC-xxx)

ID / Name / Primary actor / Goal / Trigger / Preconditions / Main flow / Alternative flows / Exception flows / Postconditions / Business rules

Reserve these for workflows with real branching or multiple actors — a single CRUD action is usually just an FR, not a full use case.

## Business Rule (BR-xxx)

A standalone statement of a constraint the business imposes, independent of any one requirement (rules often apply across several FRs). Example:

```
BR-001: A vehicle cannot have two active registrations.
BR-002: Preventive maintenance becomes due after the configured mileage interval or date interval, whichever occurs first.
```

Never invent a rule just to fill out the section — every BR should trace back to something the user said or a document supports.

## Data Requirement (DR-xxx)

Entities (User, Customer, Order, Vehicle, ...) and, for the important ones, per-field: Entity / Field / Type / Required? / Unique? / Default / Validation / Relationship.

Don't generate a full database schema unless asked — this is about what data the business needs tracked, not DDL.

## Permissions

A role × action matrix (View / Create / Edit / Delete / Approve / Export, etc.) is usually the clearest format:

| Action | Admin | Manager | Employee |
|---|---|---|---|
| View | Yes | Yes | Own data |
| Create | Yes | Yes | Limited |
| Edit | Yes | Yes | Own data |
| Delete | Yes | No | No |
| Approve | Yes | Yes | No |

Mark unknown cells explicitly as unresolved rather than guessing a plausible-looking default.

## Non-Functional Requirement (NFR-xxx)

Only cover the categories that are actually relevant to this project — don't force every category into every doc:

- **Performance** — response time, throughput, concurrency
- **Security** — authentication, authorization, encryption, audit logs, sensitive data
- **Availability** — uptime, backup, recovery
- **Scalability** — expected users, data growth, transaction growth
- **Usability** — accessibility, mobile responsiveness, ease of use
- **Maintainability** — logging, monitoring, documentation
- **Compatibility** — browsers, devices, integrations

## Integration Requirement (IR-xxx)

System / Purpose / Direction / Data exchanged / Trigger / Authentication / Frequency / Failure behavior / Dependencies

## AI Requirement (AIR-xxx)

Only write these if AI genuinely serves a business objective here — see the "don't invent" section in SKILL.md before adding this section at all.

AI use case / Business objective / Input / Output / Model requirement / Tools / Knowledge or context needed / Human approval point / Accuracy expectations / Failure behavior / Privacy / Cost considerations / Evaluation criteria

## Automation Requirement (AR-xxx)

Trigger → Condition → Action → Destination, plus failure handling, retry behavior, and where human approval sits in the flow.

## Edge Cases

Prioritize realistic ones over an exhaustive theoretical list: missing data, duplicate data, invalid data, unauthorized access attempts, failed integrations, timeouts, duplicate requests, conflicting concurrent updates, deleted/referenced records, cancelled operations, partial completion, system failure mid-process, unusual-but-real business conditions.

## Acceptance Criterion (AC-xxx)

Prefer Given/When/Then:

```
Given a vehicle has 9,900 km since its last service,
When the administrator records 10,000 km,
Then the system marks the configured maintenance interval as due.
```

## Assumption (A-xxx)

Assumption / Reason / Impact if incorrect / Needs confirmation?

Never fold an assumption into a requirement's own wording as if it were confirmed — keep it visibly separate.

## Open Question (Q-xxx)

Only questions that would materially change scope, behavior, architecture, cost, security, compliance, UX, or implementation. Five sharp questions beat thirty exhaustive ones.

## Constraint (CON-xxx) / Dependency (DEP-xxx)

Constraints: externally imposed limits (budget, timeline, regulation, existing tech). Dependencies: things this project needs from outside itself (another team's API, a data migration, a vendor contract).

## Traceability

Where it adds real value (Requirements Generation, Full SRS), connect the chain:

```
BO-001 Reduce manual maintenance tracking
  → FR-007 System calculates maintenance due status
    → UC-004 Record Vehicle Mileage
      → AC-007-1 System marks service due when mileage threshold is reached
```

Don't force a full matrix onto a five-requirement Quick Analysis — traceability earns its keep on larger specs.

### Code-to-requirement traceability (V2, when a repository is connected)

Where feasible, extend the chain down into the implementation and its verification:

```
FR-001 → API endpoint → Service → Database operation → Test
```

This gives Requirement → Implementation → Verification in one line, and is exactly what `scripts/generate_report.py --format matrix` expects as input if you want it rendered automatically.

## Evidence fields (V2)

Any requirement derived from a tool (not purely from the conversation) should carry the evidence fields defined in `evidence-model.md`: evidence type(s), source(s), and confidence. Add these as extra fields on the structures above rather than a separate parallel document — e.g. an FR gets `Evidence:` and `Confidence:` lines alongside its normal fields when it's evidence-backed.

## Structured JSON export schema

For machine-to-machine workflows, export a JSON document shaped like this. Omit arrays you have nothing for rather than emitting empty placeholders with no real content, and keep IDs consistent with the ID scheme above so the JSON and any markdown rendering stay cross-referenceable.

```json
{
  "project": {},
  "business_objectives": [],
  "stakeholders": [],
  "actors": [],
  "requirements": [],
  "business_rules": [],
  "data_requirements": [],
  "non_functional_requirements": [],
  "integrations": [],
  "ai_requirements": [],
  "automation_requirements": [],
  "assumptions": [],
  "constraints": [],
  "dependencies": [],
  "open_questions": [],
  "traceability": [],
  "evidence": []
}
```

Each entry in `requirements` should carry at minimum `{id, name, description, actor, priority}`; each entry in `evidence` should carry `{requirement_id, type, source, confidence}` (types and confidence values as defined in `evidence-model.md`). `scripts/generate_report.py` reads and writes this shape — see its `--help` for the exact expectations if you're producing this by hand for the first time on a project.
