# Output schema

Structure, field definitions, ID rules and the validation checklist for architecture documents.

## Contents
1. Standard structure
2. Required sections by depth
3. Evidence tags and gap markers
4. Field schemas
5. ID rules
6. Traceability
7. Validation checklist (manual equivalent of the scripts)

## 1. Standard structure

Produce only the sections that are relevant. If a section doesn't apply, keep the heading and write one line saying why ("Not applicable: no AI step").

```text
# Workflow Architecture: <name>
(first lines) Chain header and `Depth:` line
1 Executive Summary        14 Step Definitions        27 Scalability
2 Business Context         15 Decision Architecture   28 Cost
3 Business Objective       16 AI Architecture         29 Alternatives
4 Actors                   17 Agent Architecture      30 Trade-offs
5 Current Process          18 Tool Architecture       31 Selected Architecture
6 Target Process           19 MCP Architecture        32 Diagrams
7 Requirements             20 Data Flow               33 ADRs
8 Workflow Drivers         21 State Management        34 Risks
9 Constraints              22 Human-in-the-Loop       35 Implementation Blueprint
10 Assumptions             23 Error Handling          36 Testing Strategy
11 Quality Attributes      24 Retry & Recovery        37 Validation
12 Trigger Architecture    25 Security                38 Open Questions
13 Workflow Architecture   26 Observability
                                                        39 Handoff (optional; chain only)
```

Optimize for clarity and implementability rather than length. A simple workflow should produce a short document.

## 2. Required sections by depth

`scripts/validate_workflow.py --depth <level>` checks that a heading matching each name exists and has content (or a stated reason it doesn't apply).

| Depth | Required headings |
|---|---|
| quick | Business Objective · Workflow Architecture (with steps) · Error Handling · Assumptions · Open Questions |
| standard | quick + Requirements · Trigger Architecture · Security · Observability · Risks · Implementation Blueprint |
| full | standard + Actors · Workflow Drivers · Quality Attributes · Data Flow · Cost · Scalability · Retry & Recovery (its own heading, separate from Error Handling) · Alternatives · Selected Architecture · Diagrams · ADRs · Testing Strategy · Validation |

## 3. Evidence tags and gap markers

Facts: `[STATED]` `[DOCUMENTED]` `[OBSERVED]` `[INFERRED]` `[ASSUMED]` `[RECOMMENDED]` `[UNKNOWN]`.
Gaps: `UNKNOWN`, `NOT PROVIDED`, `REQUIRES VALIDATION`.
Recommendation classes: `REQUIRED`, `RECOMMENDED`, `OPTIONAL`, `FUTURE`, `EXPERIMENTAL`.

Tag at the row or sentence level where the origin matters (requirements' Source column, assumptions, numbers). Untagged connective prose is fine; untagged numbers and capabilities are not. The validator enforces this for money, percentages and volumes anywhere in the document (design parameters such as timeouts and retry counts are not figures in this sense, but label them `[RECOMMENDED]` in the step table's header note or the Retry section).

## 4. Field schemas

Use tables; one row per item, ID in the first column.

- **BO** — ID, objective, success measure, evidence
- **WR** — ID, description, category, source (evidence tag), priority (must/should/could/won't), rationale, acceptance criteria, dependencies
- **WD** — ID, driver, why it matters, options it eliminates, related WR
- **A** — ID, assumption, reason, impact if wrong, how to validate
- **Q** — ID, question, why it matters (what design choice depends on it), owner
- **STEP** — ID, name/purpose, type, input, output, failure behavior, retry, timeout, effect (read-only / reversible / irreversible). Dependencies come from the diagram and the state flow. Security and observability are stated once in their own sections; add a per-step note only where a step deviates. Column names stay recognizable (`Failure`, `Retry`, `Timeout`, `Type`, `Effect`). Name, type, failure, retry and timeout are required at every depth; input, output and effect from `full`. A step type containing *human*, *approval*, *wait*, *reply* or *callback* must have a real Timeout: a wait limit and a reminder or expiry path, or NOT PROVIDED plus the question that settles it.
- **DEC** — ID, decision, input, method (rule/AI/human/hybrid), output, fallback (+ AI fields: model class, prompt purpose, schema, confidence handling, validation, escalation)
- **TOOL** — see `tool-architecture.md`
- **WADR / WRISK** — see `adr-template.md`
- **TASK** — ID, component, objective, dependencies, implementation notes, acceptance criteria, testing requirements
- **TEST** — ID, type, scenario, expected result, verifies (WR/STEP/TASK)


## 5. ID rules

`PREFIX-NNN` with at least three digits (`WR-001`). Prefixes: `BO WR WD STEP DEC TOOL TASK TEST WADR WRISK A Q`. Define each ID exactly once, in the first cell of a table row, a list item, or a heading. Everywhere else is a reference. Never reuse or renumber an ID after it has been cited. Traceability and cross-reference tables should sit under a heading containing "Traceability" or "Coverage", and restated upstream material under "Carried forward from upstream", so their rows count as references, not definitions.

In a chain (`references/chaining.md`): upstream IDs (`BO`, `FR`, `NFR`, `BR`, `AIR`, `IR`, `AC`, `ADR`, `INT`, `COMP`, and earlier `A` / `Q`) are cited, never redefined; list a `BO` in a column after the first so it is a citation; `A` and `Q` continue after the highest upstream number; add an **Upstream coverage** table; carry priorities forward with a reason for any change.

## 6. Traceability

```text
BO → WR → WD → STEP → TOOL → TASK → TEST
```
Every requirement should reach a step, a task and a test. Provide a table:

| WR | WD | STEP | TOOL | TASK | TEST |
|---|---|---|---|---|---|

## 7. Validation checklist

Run by hand when scripts are unavailable. Before delivery confirm:

- [ ] Every requirement is covered by a step/decision and has acceptance criteria
- [ ] Trigger defined: source, payload, auth, validation, volume, duplicate behavior
- [ ] Inputs and outputs of consecutive steps are consistent; no hidden state
- [ ] Each AI/agent use is justified by a requirement; cheaper rung considered
- [ ] Every external call has failure behavior, retry (or reason for none), and a timeout
- [ ] Duplicate-execution risks have idempotency handling
- [ ] High-risk actions sit behind validation or human approval; the approval timeout path is defined
- [ ] Authentication, least privilege, secrets handling and AI-specific threats addressed
- [ ] Observability: correlation ID, key metrics, alerts with owners
- [ ] Cost and scale figures are labeled with their inputs; no invented prices or volumes
- [ ] No invented APIs, integrations or capabilities; unverified ones marked `REQUIRES VALIDATION`
- [ ] IDs unique, none dangling; diagrams match the step table
- [ ] Assumptions and open questions listed; no secrets anywhere
