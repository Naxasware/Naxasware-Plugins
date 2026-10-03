# Evidence model

## Contents
Evidence types, confidence, technology detection, pattern detection.

## Evidence types
Every external observation names its source and one or more types.

| Type | Meaning |
|---|---|
| USER_STATED | The user said it |
| DOCUMENTED | Written in project documentation |
| CODE_OBSERVED | Seen in source code |
| CONFIG_OBSERVED | Seen in configuration or manifests |
| DATABASE_OBSERVED | Seen in a database schema or metadata |
| API_OBSERVED | Seen in an API spec or endpoint inspection |
| INFRASTRUCTURE_OBSERVED | Seen in infrastructure definitions or cloud config |
| PROJECT_TRACKER_OBSERVED | Seen in issues, epics, milestones |
| MONITORING_OBSERVED | Seen in logging, metrics, tracing or alert setup |
| INFERRED | Concluded from other evidence; say from what |
| ASSUMED | Taken as true to proceed; must be listed as an assumption |
| RECOMMENDED | A proposal, not an observation |

Combine when several apply, for example `CODE_OBSERVED + DOCUMENTED`, and list the sources:
```
Component: Authentication Service
Evidence: src/auth/, README.md
Evidence Type: CODE_OBSERVED + DOCUMENTED
```

## Confidence
`High`, `Medium`, `Low`, `Unknown`. Confidence never replaces evidence: state the evidence, then the confidence and the reason ("repository structure inspected, runtime authorization behavior not verified").

## Technology detection
Distinguish four states and report them separately:
- **Observed**: seen working in code or config.
- **Declared**: present in a manifest (for example package.json) but usage not seen. This does not prove active use.
- **Actually Used**: imports, calls or configuration show real use.
- **Unknown**: not enough evidence.
Do not assume a cloud provider merely because a dependency exists; require provider configuration.

## Pattern detection
Name an architectural style (layered, MVC, modular monolith, microservices, clean, hexagonal, event-driven, serverless, CQRS) only with evidence: dependency direction, deployment units, message flows, data ownership. A folder name alone is not evidence. Record the pattern with its evidence list and confidence.
