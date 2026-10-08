# Drift, consistency, traceability, impact and debugging

## Contents
1. Drift detection
2. Architecture consistency
3. Extended traceability
4. Change impact analysis
5. Debugging a failing workflow
6. Anti-pattern scan for existing workflows

## 1. Drift detection

Compare three views of the same workflow: **documented** (docs, diagrams, tickets), **configured** (workflow definition, config, infrastructure) and **observed** (code, executions, logs). Each difference is one drift record, numbered `DRIFT-001`, `DRIFT-002`, ... (defined once, referenced elsewhere).

Each record has all seven fields:

```text
### DRIFT-001 <short title>
- Drift:               what differs
- Expected:            what the reference view says (name the view and source)
- Observed:            what was actually found (name the source)
- Evidence:            evidence type, source, confidence
- Impact:              what this changes for behavior, users or operations
- Risk:                low / medium / high and why
- Recommended Action:  REQUIRED / RECOMMENDED / OPTIONAL / FUTURE, and the action
```

Typical drift: undocumented step, undocumented API or database dependency, missing retry, different AI model, changed prompt, missing approval, outdated diagram. Report only drift you can support; "documentation looks old" is not a record. State which view you treated as the reference. If a view was not available, say the comparison was not possible instead of recording drift against it.

## 2. Architecture consistency

Check the chain for contradictions:

```text
Requirements -> Workflow architecture -> Workflow configuration -> Code
-> Infrastructure -> Monitoring -> Documentation
```

For each adjacent pair that you can see, list contradictions (a requirement with no step; a step with no implementation; an implementation with no documentation; an alert for a step that no longer exists). Skip layers you cannot inspect and list them under Missing Evidence.

## 3. Extended traceability

V1 chain: `BO -> WR -> WD -> STEP -> TOOL -> TASK -> TEST`. For existing systems add the implementation links:

```text
STEP-### -> File -> Function -> Service -> External dependency
STEP-### -> TEST-###
```

Test coverage per step or path: `COVERED`, `NO_TEST`, `PARTIAL_COVERAGE`, `UNKNOWN`. Use `UNKNOWN` when tests were not inspected. Put these tables under a heading containing "Traceability" so the ID validators count rows as references. Where a project tracker exists, add `Workflow problem -> Issue -> Task -> Implementation` links.

## 4. Change impact analysis

When a component changes (a step, tool, prompt, model, schema, API version, credential, schedule):

```text
Changed component -> Dependent steps -> Dependent tools -> Data -> APIs -> Agents
-> Tests -> Monitoring -> Business processes
```

Produce an impact report: for each downstream layer list what is affected and the evidence; mark what could not be checked. Add the validation needed before and after the change, and a rollback path.

## 5. Debugging a failing workflow

```text
Failure -> Execution context -> Failed step -> Input -> Dependency -> Error
-> Root-cause candidates -> Evidence -> Fix options -> Validation
```

Rules:

- Describe the failure first (what, when, how often, since when) from execution evidence, not from the report of it.
- List root-cause candidates ranked, each with the evidence for and against. Say "candidate" until an observation separates it from the rest.
- **Never claim a root cause without evidence.** If evidence is missing, say what observation would confirm or exclude each candidate.
- Fix options carry trade-offs and a validation step. Do not change the system; recommend.
- Common culprits to check: duplicate delivery without idempotency, missing timeout, unbounded retries, schema change upstream, expired credential, rate limiting, model output off-schema, loop without termination, hidden state.

## 6. Anti-pattern scan for existing workflows

Use `workflow-patterns.md` and add these checks: AI where deterministic logic is enough; an agent where one AI call is enough; multiple agents where one suffices; RAG without a retrieval need; MCP without a tool or context need; excessive integrations; missing retries, timeouts, idempotency or validation; excessive permissions; secrets in configuration; undocumented dependencies; giant workflows; excessive branching; loops without termination; no monitoring; no recovery strategy. Each finding cites evidence or is marked `INFERRED`.
