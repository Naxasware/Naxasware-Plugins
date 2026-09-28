# Analysis workflows

## Contents
Observed architecture, traceability, drift, debt, modernization, migration strategies, change impact.

## Observed architecture
From evidence, list components, layers, integrations and data stores, each with evidence type and confidence. Keep observed and recommended in separate sections.

## Traceability
- Requirement -> module -> implementation -> test, with a confidence per link (for example FR-014 -> src/orders/ -> OrderService -> order.test.ts).
- Architecture component -> repository location -> implementation -> configuration -> deployment. Gaps reveal missing implementation, unexpected implementation, or drift.
- Decisions: requirement -> driver -> decision -> component -> implementation, and requirement -> evidence -> decision where evidence exists.

## Drift detection
Workflow: current documentation -> repository analysis -> infrastructure analysis -> observed architecture -> comparison -> drift report -> updated architecture.
Look for undocumented components, removed components, changed dependencies, new integrations, inconsistent boundaries, outdated diagrams, obsolete documentation.
```
DRIFT-001
Expected: Service A -> Service B
Observed: Service A -> Database directly
Impact: Architecture documentation may be outdated.
Evidence: <files>   Confidence: <level>
```

## Architecture debt
Look for excessive coupling, unclear boundaries, duplicated responsibilities, shared-database problems, circular dependencies, infrastructure complexity, missing abstraction, tightly coupled integrations, deployment bottlenecks. Categorize each item `Confirmed`, `Likely` or `Potential`, with evidence.

## Modernization
Current state -> problems -> constraints -> target state -> migration strategy -> transition architecture -> phased implementation -> risk controls. Do not recommend a full rewrite by default; justify it if you do.

## Migration strategies
Evaluate when relevant: strangler pattern, modularization, incremental extraction, database migration, API facade, parallel run, phased replacement, branch-by-abstraction, rebuild. For each: when it fits, trade-offs, risk, effort.

## Change impact
Input: a proposed change (for example local file storage to object storage). Walk: application, database, API, authentication, permissions, uploads, downloads, background jobs, deployment, monitoring, cost, migration, backup.
Output table: Affected component | Impact | Required change | Risk | Migration step.
