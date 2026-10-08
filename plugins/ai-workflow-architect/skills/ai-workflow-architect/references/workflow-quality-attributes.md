# Quality attributes

Evaluate the ones that matter for this workflow; skip the rest and say why. For each, convert a vague wish into a measurable target, or record "target not defined" — never write "should be fast" into a requirement.

| Attribute | Question | Make it measurable | Common tension |
|---|---|---|---|
| Reliability | Does it complete correctly? | Success rate over N executions; no duplicate side effects | Cost, latency (retries, validation) |
| Availability | Can it run when needed? | Window and tolerated downtime; trigger loss handling | Cost of redundancy |
| Resilience | Does it recover from failure? | Recovery time; no lost items after outage | Complexity (queues, persisted state) |
| Performance | How fast must it finish? | p50/p95 end-to-end; per-step budget; async acceptable? | Reliability, AI depth |
| Scalability | How many executions? | Executions/day, peak, concurrency, payload size | Cost, simplicity |
| Cost efficiency | Cost per execution? | Cost per run with labeled inputs; monthly ceiling | Quality (cheaper model), latency |
| Security | Are data and tools protected? | Named threats mitigated; least-privilege scopes | Convenience, speed |
| Observability | Can we see what happened? | Every run traceable by correlation ID; alerts on named failures | Log cost, privacy |
| Maintainability | Can people change it safely? | Who owns it; step count; documented rules | Flexibility |
| Testability | Can steps be tested alone? | Pure steps; mockable integrations; AI evals | Speed of delivery |
| Auditability | Can decisions be traced? | Who/what/when/why recorded; retention period | Privacy, storage |
| Explainability | Can AI decisions be understood where required? | Reason/evidence captured with each AI decision | Model choice, latency |
| Determinism | Are results predictable where required? | Same input → same output for rule steps; bounded variance for AI | Use of AI |

How to use: pick the three to five that drive the design (these become `WD-` drivers), give each a target or an explicit "not defined," and revisit them when comparing alternatives — alternatives differ precisely in which attributes they trade away.
