# Testing strategy

Tests get `TEST-` IDs and link to the requirements and tasks they verify (traceability: WR → … → TASK → TEST).

| Type | What it checks |
|---|---|
| Unit | Individual functions/steps: transformations, validation, routing rules |
| Integration | Real or sandboxed external APIs/services: auth, schemas, rate limits |
| Workflow | The complete path end to end for representative inputs, including each branch |
| Failure | Timeouts, API errors, invalid input, duplicate trigger, exhausted retries, dead-letter handling |
| AI | Prompt/output validity, accuracy on a labeled set, regression after prompt or model change, tool selection |
| Security | Permissions (can the step do only what it should?), malicious/injected input, secret leakage |
| Load | Expected and peak volume, concurrency, rate-limit behavior |
| Recovery | Resume after crash mid-run without duplicate side effects |
| Human approval | Approve, reject, modify, timeout and escalation paths |

Guidance:
- Make steps testable in isolation: pure logic separated from integrations; integrations behind adapters you can fake.
- Test the unhappy paths as deliberately as the happy path — most production incidents live there.
- For AI steps, deterministic assertions first (schema, enum, bounds), then evaluation sets; fix the evaluation set so changes are comparable.
- Each requirement's acceptance criteria should map to at least one test; say so in the traceability table.
