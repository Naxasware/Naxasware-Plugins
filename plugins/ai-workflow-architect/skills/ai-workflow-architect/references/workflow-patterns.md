# Workflow patterns and anti-patterns

Use a pattern because the requirement calls for it, not because it appears on a list.

## Contents
1. Patterns
2. Anti-patterns to detect

## 1. Patterns

| Pattern | Use when | Watch out |
|---|---|---|
| Sequential | Steps depend on each other | Long chains compound failure probability |
| Branching / conditional routing | Different input → different path | Too many branches become unreadable; consider a router step with a table |
| Fan-out / fan-in | Independent work can run in parallel then merge | Define partial-failure behavior and aggregation timeout |
| Loop | Process a collection or poll | Always bound iterations and time |
| Map/reduce | Same operation over many items, then combine | Memory/payload size; per-item failure handling |
| Pipeline | Fixed series of transformations | Version the intermediate schema |
| Queue-based processing | Decouple producer/consumer, absorb bursts | Adds infrastructure and ordering/duplication concerns; justify with volume or burst driver |
| Event-driven | Many consumers, loose coupling | Harder to trace; needs correlation IDs |
| Saga / compensation | Multi-system change that must be undone on failure | Compensations can fail too; design them idempotent |
| Approval workflow / human-in-the-loop | Risky or low-confidence decisions | Needs timeout, escalation, default-safe outcome |
| Retry | Transient failure | Backoff + jitter; idempotency |
| Dead-letter | Items that exhaust retries | Someone must own the DLQ |
| Circuit breaker | Dependency is failing; stop hammering it | Define the fallback while open |
| Fallback | Degraded alternative exists | Make the degraded mode visible |
| Caching | Repeated identical reads/AI calls | Staleness and invalidation; never cache sensitive data carelessly |
| Batching | Reduce per-call overhead or cost | Latency vs cost; partial-batch failure |
| Debounce | Collapse bursts of the same event | Window length vs responsiveness |
| Rate limiting | Protect your own or a vendor's limits | Queue or drop? decide |
| Async processing | Work longer than a request should wait | Need status/callback and result retrieval |

## 2. Anti-patterns to detect

Scan every design (new or existing) for these. Report each with the location, why it hurts, and the fix.

| Anti-pattern | Why it hurts |
|---|---|
| Unnecessary AI | Adds cost, latency, nondeterminism where a rule works |
| Unnecessary agents / multi-agent | Unpredictable path, hard to test, larger attack surface |
| Giant workflow | One failure story for everything; split by responsibility |
| Hidden state | Behavior depends on something no step declares |
| Circular dependencies / infinite loops | Runaway cost and stuck executions; bound loops |
| No retry strategy / missing timeout | Transient failures become outages; stalls |
| Duplicate side effects | Retries and replays send twice, charge twice |
| Hardcoded credentials | Leak and rotation problems |
| Excessive tool permissions | An agent or compromised step can do more than needed |
| Unvalidated AI output | Malformed or manipulated output flows into business actions |
| No human approval for high-risk actions | Irreversible mistakes at machine speed |
| Vendor lock-in without consideration | Migration cost surprise; note it as a trade-off, don't reflexively avoid |
| Overuse of webhooks | Fragile chains of callbacks; consider a queue or polling where appropriate |
| Synchronous long-running processes | Timeouts and dropped connections; use async |
| Excessive branching | Untestable path explosion |
| Poor observability | Cannot tell why a run failed |
| Undocumented business rules | Rules live only in someone's head or inside a prompt |
