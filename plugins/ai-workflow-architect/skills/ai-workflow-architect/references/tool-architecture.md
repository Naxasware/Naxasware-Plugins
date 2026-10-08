# Tool and integration architecture

Applies to anything a workflow or agent calls: APIs, databases, browsers, search, internal services, CRM/ERP, email, messaging, storage, payment systems, code execution, business apps, MCP tools.

## Specification per tool

```text
Tool ID            TOOL-001
Name
Purpose
Input / Output     (schemas)
Authentication     (method; which secret store; never the secret)
Permissions        (scopes needed — least privilege)
Failure modes      (timeouts, 4xx/5xx, rate limit, schema drift, partial result)
Rate limits        (known value or REQUIRES VALIDATION)
Timeout
Side effects       (none / reversible / irreversible)
Idempotency        (native key / safe upsert / needs dedupe)
Security           (data sent, data returned, logging redaction)
```

## Rules

- **Don't assume an integration exists.** If you haven't been told or shown that a system has an API, a connector, or a given endpoint, write `REQUIRES VALIDATION`. Never invent endpoints, fields, scopes or limits.
- **Separate read from write.** Give reading and mutating capabilities separate credentials or tools so a read-only step can't change data.
- **Classify side effects.** Irreversible tools (send, pay, delete, publish) sit behind validation or approval and idempotency protection.
- **Define the contract.** Input/output schemas with required fields and validation, so schema drift fails loudly at the boundary.
- **Plan for the tool being down.** Each tool has a stated degraded behavior: retry, queue, fall back, park, alert.
- **Wrap, don't scatter.** If several steps call the same system, one adapter/tool definition owns auth, retries, rate limiting and logging.
- **Prefer fewer tools.** Each tool an agent can see is attack surface and a chance to choose wrongly.

## Integration checklist

Authentication method and token lifetime/refresh; permission scopes; rate limits and burst behavior; pagination; webhook signature verification; data format and versioning; sandbox/test environment availability; contract/SLA if relevant; who owns the integration.
