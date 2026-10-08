# Observability

If you can't tell why a run failed, the workflow is not production-ready. Observability is designed in, not added after the first outage.

## Logs
Structured (not free text), one record per significant event: run start/end, step start/end/outcome, retries, decisions (including AI decision inputs-by-reference and outputs), approvals (who, when, what), errors with classification. Include a **correlation ID** carried through every step and tool call. Redact PII and secrets; log references instead of payloads where sensitive.

## Metrics
Execution count, success rate, failure rate (by category), end-to-end and per-step latency, retry count, queue depth/age, human-approval wait time, token usage, cost per run, tool error rate, AI confidence or review-rate where defined.

## Traces
Follow a run end to end: workflow → step → tool → AI call → database → external API. Needed whenever more than a couple of steps or systems are involved or when debugging latency.

## Alerts
Define thresholds only where someone will act: sustained failure rate, no executions when expected (silent trigger failure), dead-letter growth, approval backlog, cost spike, auth expiry. Each alert names an owner and a first action. Too many alerts get ignored.

## Audit
Where decisions must be explainable or regulated, keep an immutable record of inputs-by-reference, decision, who/what decided, and outcome, for a stated retention period.

## AI-specific
Record model/version, prompt version, token counts, latency, validation outcome, fallback taken. Sample outputs for human review. Track drift in review-rate or validation failures.
