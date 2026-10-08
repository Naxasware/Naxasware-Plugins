# Evidence model

How to record, grade and report what you know about an existing workflow. Applies whenever you inspect something real (a workflow export, repository, API, database, infrastructure, logs, tickets) or compare it with what people say about it.

## Contents
1. Evidence types
2. Evidence record
3. Confidence
4. Observed vs documented vs recommended
5. Technology detection states
6. Evidence report layout

## 1. Evidence types

| Type | Meaning |
|---|---|
| `USER_STATED` | The user said it |
| `DOCUMENTED` | A supplied document, diagram, runbook or ticket says it |
| `WORKFLOW_OBSERVED` | Seen in a workflow definition or export on an automation platform |
| `CODE_OBSERVED` | Seen in source code |
| `CONFIG_OBSERVED` | Seen in configuration, manifests, environment definitions (values masked) |
| `DATABASE_OBSERVED` | Seen in a schema, row counts or execution/state tables (read-only) |
| `API_OBSERVED` | Seen in an API spec, response or documentation endpoint |
| `INFRASTRUCTURE_OBSERVED` | Seen in cloud, container, queue, scheduler or CI/CD definitions |
| `MONITORING_OBSERVED` | Seen in logs, metrics, traces or execution history |
| `PROJECT_TRACKER_OBSERVED` | Seen in an issue, task or project document |
| `INFERRED` | Reasoned from the above; say from what |
| `ASSUMED` | A labeled guess with the impact if wrong |
| `RECOMMENDED` | Your proposal, not a fact about the current system |
| `UNKNOWN` | Not known and not yet found |

The short tags of the V1 method (`[STATED]`, `[DOCUMENTED]`, `[OBSERVED]`, `[INFERRED]`, `[ASSUMED]`, `[RECOMMENDED]`, `[UNKNOWN]`) remain valid in running prose. Use the long names in evidence tables and drift records because they say *where* the fact came from. Map: `[OBSERVED]` is any of the `*_OBSERVED` types, `[STATED]` is `USER_STATED`.

## 2. Evidence record

Every important discovered fact gets five parts:

| Evidence Type | Source | Confidence | Observation | Interpretation |
|---|---|---|---|---|

- **Source**: a path, workflow name, node/step name, endpoint, table, log query or ticket ID. Specific enough that someone else can find it again.
- **Observation**: what was literally seen. No judgement.
- **Interpretation**: what you conclude from it. Keep apart from the observation so a reader can disagree with the conclusion without doubting the fact.

Do not record every file you opened. Record the facts the architecture or a finding depends on.

## 3. Confidence

`HIGH` directly observed in the authoritative place and unambiguous. `MEDIUM` observed but indirect, partial or possibly stale. `LOW` inferred, or observed in a non-authoritative place. `UNKNOWN` could not be established.

Rules: `INFERRED`, `ASSUMED` and `RECOMMENDED` are never `HIGH`. A single log line is not evidence of a rate. A configured thing is not evidence that it runs.

## 4. Observed vs documented vs recommended

Three separate layers, never merged in one sentence:

- **Documented**: what people wrote down.
- **Observed**: what the inspected artifacts actually contain or did.
- **Recommended**: what you propose.

Write "the document says retries are enabled; the workflow definition has no retry setting on `STEP-004`" rather than "retries are missing" or "retries are enabled". Where the layers disagree, that is a drift record (`drift-and-consistency.md`).

## 5. Technology detection states

For any technology the system supposedly uses, classify:

| State | Meaning |
|---|---|
| Declared | Documentation or configuration says it is used |
| Observed | The repository or infrastructure actually contains it |
| Active | Evidence suggests it is in use now (recent executions, live references, current traffic) |
| Unused | Configured or imported but not meaningfully used |
| Unknown | Cannot be verified |

Never write "the system uses X" without at least `Observed`, and say `Active` only with execution or runtime evidence. Declared-only means `REQUIRES VALIDATION`.

## 6. Evidence report layout

```text
# Evidence Report
## Verified        facts confirmed in the authoritative source (HIGH)
## Observed        facts seen directly, with source
## Documented      claims from documents, not yet checked against the system
## Inferred        conclusions, with what they rest on
## Assumed         labeled guesses with impact if wrong
## Unknown         things that could not be established
## Conflicts       places where layers disagree (link DRIFT records)
## Missing Evidence  what to obtain next and why it would change the answer
```

Empty sections stay with one line saying so.
