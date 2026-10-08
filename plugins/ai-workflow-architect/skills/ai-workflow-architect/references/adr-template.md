# ADR and risk templates

## Architecture decision record (`WADR-`)
Use for decisions where a reasonable team could have chosen otherwise: AI vs rules, agent vs pipeline, platform, queue vs direct call, build vs buy, sync vs async.

```text
Decision ID:          WADR-001
Decision:             <one sentence>
Context:              <situation and constraints, with evidence tags>
Problem:              <what must be decided>
Options:              A ... / B ... / C ...
Evaluation criteria:  <drivers WD-xxx and quality attributes used>
Selected approach:    <option>
Rationale:            <why this wins on the criteria>
Advantages:
Disadvantages:
Risks:                <WRISK-xxx refs>
Consequences:         <what this makes easier/harder later>
Related requirements: <WR-xxx>
```

Keep ADRs short. Record a rejected option and why, so it isn't re-litigated. If a decision rests on an assumption, reference its `A-` ID.

## Risk (`WRISK-`)
```text
Risk ID:      WRISK-001
Description:
Cause:
Impact:
Likelihood:   low / medium / high, or UNKNOWN  (no invented percentages)
Severity:     low / medium / high
Mitigation:
Contingency:
Owner:        <if known, else NOT PROVIDED>
```
Rate qualitatively unless the user supplied data. Tie each risk to a requirement, step or assumption where possible.
