# Cost and scalability

## Cost components
Workflow execution/platform fees; API calls; LLM tokens (input and output); embeddings; storage; database; infrastructure; observability; third-party SaaS; human operational cost (review time, on-call).

## Estimating honestly
Cost per execution = Σ(step cost). For AI steps: (input tokens × input price) + (output tokens × output price) × calls per run. Show inputs in a table:

| Input | Value | Evidence |
|---|---|---|
| Executions/day | e.g. 500 | `[ASSUMED]` or `[STATED]` |
| Tokens per AI call | e.g. 1,200 in / 200 out | `[ASSUMED]` |
| Price per 1M tokens | REQUIRES VALIDATION | provider price page |

Where a price or volume is unknown, state the **formula and the unknowns** rather than inventing a number. A labeled range beats a precise-looking guess. Include human cost: a review step at 20% of runs can dominate token cost.

## Cost levers (and what they trade)
Skip AI where rules suffice; smaller model for easy cases with escalation; caching identical requests; batching; shorter context/retrieval of fewer chunks; avoid re-running unchanged work; sampling for evaluation. Each lever trades quality, latency or complexity — say which.

## Scalability analysis
Estimate or ask for: executions/day, peak executions, concurrency, payload size, vendor API rate limits, AI requests and token volume, queue depth, database throughput, storage growth. Then find the **first bottleneck** (often a vendor rate limit or a serial step), not every conceivable one. Remedies in order of necessity: remove serial waits, batch, parallelize with bounded concurrency, add a queue (only with a burst or decoupling driver), scale the datastore. Recommend infrastructure (queues, clusters, microservices) only where the numbers require it.
