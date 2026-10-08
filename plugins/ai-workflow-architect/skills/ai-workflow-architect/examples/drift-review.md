# Workflow Review: invoice intake (invented scenario)

Type: review report (not a design document; validate with validate_evidence.py)
Mode: Existing workflow analysis + Drift detection
Scope: a fictional invoice-intake workflow on an automation platform plus its design document. All names, tables and numbers are invented for illustration.

## Executive Summary
The documented design says invoices are classified by an LLM, validated, and sent for approval above a threshold. The exported workflow matches that outline but differs in three places that affect reliability and approval. No execution history was supplied, so no rate or cost statements are made.

## Evidence Report

### Verified
- The workflow export contains a webhook trigger, one LLM node, a validation node and an approval branch (WORKFLOW_OBSERVED, HIGH).

### Observed

| Evidence Type | Source | Confidence | Observation | Interpretation |
|---|---|---|---|---|
| WORKFLOW_OBSERVED | export `invoice-intake.json`, node "Classify" | HIGH | LLM node uses model name `model-a-small`; no fallback branch | Single point of failure on the model call |
| WORKFLOW_OBSERVED | export, node "Create bill" | HIGH | No retry setting and no timeout on the HTTP node | Transient accounting-API errors will fail the run |
| WORKFLOW_OBSERVED | export, node "Approve" | HIGH | Approval node is skipped when `amount` is empty | Missing amount bypasses approval |
| CONFIG_OBSERVED | export, credential reference `accounting-api` | MEDIUM | Credential referenced by name; value `API_KEY=********` masked | Secret handled by reference, no exposure seen |

### Documented

| Evidence Type | Source | Confidence | Observation | Interpretation |
|---|---|---|---|---|
| DOCUMENTED | design doc section 4 | MEDIUM | "Model B is used for classification" | Doc may predate a model change |
| DOCUMENTED | design doc section 6 | MEDIUM | "Failed bill creation is retried three times" | Expectation of retry behavior |
| DOCUMENTED | design doc section 7 | MEDIUM | "All invoices above the approval limit need approval" | Expected approval rule |

### Inferred
- The prompt was probably changed together with the model; INFERRED from the node history being absent, LOW confidence.

### Assumed
- A-001 The approval limit in the doc is current. Impact if wrong: drift record DRIFT-003 changes severity.

### Unknown
- Execution volume, failure rate and cost: no logs supplied.
- Test coverage: tests were not provided.

### Conflicts
See DRIFT-001 to DRIFT-003.

### Missing Evidence
- Execution history for the last 30 days would confirm whether retries are applied at platform level.
- The test suite or test plan for the approval branch.

## Workflow Drift

### DRIFT-001 Classification model differs from documentation
- Drift: the model named in the workflow differs from the documented model
- Expected: "Model B" (design doc section 4, DOCUMENTED)
- Observed: `model-a-small` (export, node "Classify", WORKFLOW_OBSERVED, HIGH)
- Evidence: WORKFLOW_OBSERVED, export node "Classify", HIGH
- Impact: classification accuracy and cost assumptions in the doc may not hold
- Risk: medium, because accuracy targets were set against the documented model
- Recommended Action: RECOMMENDED. Confirm which model is intended, then update the doc or the node and re-run the classification evaluation.

### DRIFT-002 Documented retries are not configured
- Drift: no retry on bill creation
- Expected: three retries (design doc section 6, DOCUMENTED)
- Observed: no retry or timeout setting on the node (export, WORKFLOW_OBSERVED, HIGH)
- Evidence: WORKFLOW_OBSERVED, export node "Create bill", HIGH; platform-level defaults not verified
- Impact: transient errors from the accounting API fail the invoice run
- Risk: high, because failed runs may leave invoices unbilled without an alert
- Recommended Action: REQUIRED. Add a bounded retry with backoff and a timeout, plus duplicate protection on bill creation before enabling retries.

### DRIFT-003 Approval is skipped when the amount is empty
- Drift: approval rule has an unguarded bypass
- Expected: every invoice above the limit is approved (design doc section 7, DOCUMENTED)
- Observed: the approval node is skipped when `amount` is empty (export, node "Approve", WORKFLOW_OBSERVED, HIGH)
- Evidence: WORKFLOW_OBSERVED, export node "Approve", HIGH
- Impact: an invoice with a missing or unparsed amount reaches bill creation without approval
- Risk: high, because the bypass affects a financial action
- Recommended Action: REQUIRED. Route empty or unparsable amounts to manual review before the approval check.

## Recommendations

| Class | Recommendation | Reason | Evidence | Expected Benefit | Trade-off |
|---|---|---|---|---|---|
| REQUIRED | Guard the approval branch against empty amounts | DRIFT-003 | WORKFLOW_OBSERVED, HIGH | Closes an approval bypass | Adds a manual-review queue |
| REQUIRED | Add retry, timeout and duplicate protection to bill creation | DRIFT-002 | WORKFLOW_OBSERVED, HIGH | Fewer silent failures | Needs an idempotency key from the accounting side (REQUIRES VALIDATION) |
| RECOMMENDED | Reconcile the model name with the doc and re-evaluate | DRIFT-001 | WORKFLOW_OBSERVED, HIGH | Accurate doc and targets | One evaluation run |

## Open Questions
- Q-001 Which classification model is intended? Decides whether DRIFT-001 is a doc fix or a workflow fix.
- Q-002 Does the accounting API accept an idempotency key? Decides how retries can be made safe.
