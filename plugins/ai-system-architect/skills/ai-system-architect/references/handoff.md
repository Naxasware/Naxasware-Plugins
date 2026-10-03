# Developer handoff

## Contents
Handoff contents, task breakdown, testing strategy, final answer skeleton.

## Handoff order
Architecture overview -> project structure -> component responsibilities -> data model -> API contracts -> integration contracts -> security requirements -> infrastructure -> environment variables (names only, never values) -> deployment -> testing strategy -> observability -> implementation phases.

## Architecture is not implementation
Provide folder structures, pseudocode, interface definitions, API contracts, schemas and implementation tasks. Do not generate an entire production application from architecture mode; keep architecture and implementation separate.

## Task breakdown
```
ARCH-001  Create authentication boundary   (component: COMP-00x, ADR-00y)
ARCH-002  Implement tenant context
```
Each task references an architecture component or ADR.

## Testing strategy
Choose only what the architecture's risks call for: unit, integration, API, contract, end-to-end, performance, security, resilience, AI evaluation. Tie each to a risk ID.

## Final answer skeleton (adapt, keep it short)
1. Summary and mode.
2. Evidence used and what was not inspected.
3. Observed architecture (if any), with evidence types and confidence.
4. Findings / gaps / drift / debt.
5. Options, trade-offs, selected architecture and rationale.
6. Recommendations with classification.
7. ADR candidates, risks, diagrams.
8. Roadmap or handoff.
9. Assumptions and open questions.
