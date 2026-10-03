# Comparison and validation

## Comparing options
For monolith vs modular monolith vs microservices, PostgreSQL vs MongoDB, cloud vs self-hosted, or any comparison, tie each row to a requirement:
Requirement | Option A | Option B | Trade-off | Risk | Operational impact | Cost driver | Complexity.
Do not declare a universal winner. Recommend for this context and say what would change the recommendation.

## Validating a designed architecture
Check and report status per area: requirements coverage, quality attributes, security, data, integration, failure handling, scalability, observability, cost, team capability, operational complexity.
Table: Requirement | Architecture response | Status | Evidence / rationale.
Status values only: `Covered`, `Partially Covered`, `Not Covered`, `Unknown`. Areas: requirements, security, performance, scalability, reliability, data, integrations, observability, AI, operations, cost. Do not create numerical scores.

## Consistency checks
Compare requirements, architecture, diagrams, ADRs, technology stack, implementation, infrastructure. Report contradictions (for example an ADR choosing PostgreSQL while a diagram shows MongoDB). Run `scripts/validate_diagrams.py` for diagram-versus-architecture agreement.

## Recommendation classes
REQUIRED, RECOMMENDED, OPTIONAL, FUTURE, EXPERIMENTAL. Use REQUIRED only when a requirement or a confirmed risk demands it.
