# Modes and Output Templates

## The six analysis modes

These describe *what kind of input/task you're dealing with*, not a document format — pick the one that matches what's in front of you (a request can span more than one).

1. **Discovery** — user has only an idea. Output: problem statement, business objective, stakeholders, initial scope, assumptions, unknowns, discovery questions.
2. **Requirements Extraction** — user gave existing information (notes, a process description, a document). Extract actors, processes, requirements, business rules, constraints, dependencies, assumptions, gaps — don't re-ask for what's already there.
3. **Requirements Analysis / Audit** — user gave an existing requirements doc and wants it checked. Check completeness, consistency, ambiguity, contradictions, testability, feasibility, scope, and missing edge cases/roles/permissions/NFRs. See `quality-framework.md`.
4. **Requirements Generation** — produce a complete spec from whatever's available.
5. **MVP Definition** — sort functionality into must-have / should-have / future / out-of-scope, anchored to the business objective, not to what's easiest to build.
6. **Change Analysis** — user is changing an existing requirement. Identify what's affected: requirements, workflows, roles, business rules, data, integrations, acceptance criteria, and possible scope implications. Don't just describe the new requirement — trace its ripple effects through the rest of the spec.

### V2-only modes (require tool access to an existing system)

7. **Existing-System Reconstruction** — no (or unreliable) documentation exists; build the As-Is picture from the system itself. Discovery path: repository → architecture → modules → data → users/roles → existing workflows → integrations → observed behavior → requirements reconstruction. Output an **As-Is System Specification**: modules, roles, workflows, data entities, APIs, integrations, business rules, observed behavior, technical constraints — each item carrying its evidence per `evidence-model.md`. Especially useful for inherited/legacy codebases and modernization work.
8. **Requirements-vs-Implementation Comparison** — documented requirements exist *and* the system is connected; classify each documented requirement as Implemented / Partially Implemented / Not Implemented / Conflict, and surface Implementation-without-documented-requirement separately as undocumented functionality. See `evidence-model.md` for the classification and reporting formats.

## The eight output shapes

Match the shape to what the user actually needs, not to how impressive a longer document looks:

| Shape | When to use it |
|---|---|
| Quick Analysis | A short, structured answer — a few key points, not a full document |
| Discovery Report | Early-stage idea, mode 1 |
| Full SRS | Comprehensive spec, most/all of the Standard Output Package below |
| Developer Handoff | Implementation-focused; heavy on FR/BR/DR/AC, light on business narrative |
| Product Brief | Business/product-focused; heavy on objective, scope, MVP, light on field-level detail |
| Requirements Audit | Review of an existing spec — findings-oriented, mode 3 |
| MVP Specification | Focused on first release only |
| Change Impact Report | Mode 6 output — what changed and what it touches |
| As-Is System Specification | Mode 7 output — reconstructed picture of an existing/legacy system |
| Requirements Diff | Two requirement sets compared: Added / Removed / Changed / Unchanged / Potential conflicts, by stable ID |

If the user hasn't said which shape they want, infer from their input and say what you picked ("Since this is just an idea, here's a Discovery Report — let me know if you want it developed into a full spec").

## Change Impact Report format

Per affected artifact (requirements, users/permissions, state machine/workflow, data, integrations/APIs, reports, security, tests, documentation):

```
Affected artifact:
Impact:
Reason:
Required change:
Risk:
Priority:
```

## Export formats

V2 can render the same underlying analysis into: Markdown (default for anything a human reads), JSON (schema in `requirement-schema.md`, for machine-to-machine use), CSV (flat matrices — traceability, requirement lists), Full SRS, Developer Handoff, Requirement Matrix, Traceability Matrix, and Change Impact Report. Don't force every format for every request — pick the one the user actually needs, or ask if it's genuinely unclear. `scripts/generate_report.py` renders Markdown/CSV/traceability-matrix output from a JSON source that follows the schema in `requirement-schema.md`.

## Standard Output Package (for Full SRS / Requirements Generation)

Only include sections you have real content for. Clearly label sections that are skipped for lack of information rather than quietly dropping them — the user should be able to tell "not applicable" apart from "not covered yet."

```
01 Executive Summary
02 Problem Statement
03 Business Objectives
04 Scope
05 Out of Scope
06 Stakeholders
07 Actors & Roles
08 Current-State Process
09 Future-State Process
10 Functional Requirements
11 User Stories
12 Use Cases
13 Business Rules
14 Data Requirements
15 Permissions
16 Non-Functional Requirements
17 Integrations
18 AI Requirements
19 Automation Requirements
20 Edge Cases
21 Acceptance Criteria
22 Prioritization
23 Assumptions
24 Constraints
25 Dependencies
26 Open Questions
27 Traceability Matrix
28 MVP Recommendation
29 Requirements Quality Assessment
30 Next Steps
```

For a Quick Analysis, Discovery Report, or Developer Handoff, pick the subset that fits — you don't need all 30 sections for a one-page idea.

## Current-state / future-state process notation

When there's a real existing process to document:

```
AS-IS: Trigger → Step → Decision → Action → Outcome
TO-BE: Trigger → System/User Action → Validation → Business Rule → Decision → Automation → Outcome
```

For AS-IS, only claim an inefficiency (duplication, delay, error-prone step, bottleneck) if the user's description actually supports it — don't assume the old process was bad just because it's manual.

For TO-BE, clearly separate three things that are easy to blur together: what's *required* behavior, what's a *recommended* improvement, and what's *optional* automation the user could add later.
