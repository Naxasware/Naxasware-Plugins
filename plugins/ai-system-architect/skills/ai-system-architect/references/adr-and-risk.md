# ADRs and risk register

## ADRs
Generate ADR candidates only for significant decisions, typically: architecture style, database, authentication, async processing, AI model strategy. Do not produce dozens of trivial ADRs.
```
ADR-001: <title>
Status: Proposed
Context: <drivers and constraints, with requirement IDs>
Options considered: <A, B, C with one-line trade-offs>
Decision: <choice>
Consequences: <benefits, costs, follow-ups>
Classification: REQUIRED | RECOMMENDED | OPTIONAL | FUTURE | EXPERIMENTAL
Evidence: <sources and types>
```

## Risk register
```
RISK-001
Risk:
Evidence:
Impact:
Likelihood:
Mitigation:
Contingency:
Affected component:
```
Every risk names an affected component and cites evidence or states that it is an assumption. Testing recommendations must map to these risks.
