# Examples

`chain-example/` runs one fictional project (supplier invoice intake and approval) through all three plugins. It is used both as documentation and as the chain regression fixture in `ci-smoke.sh`.

| File | Stage | Produced by |
|---|---|---|
| `01-requirements.md` | 1 | `ai-requirements-analyst`: chain header, evidence labels, a client conflict kept open (CONFLICT-001), acceptance criteria for every FR, handoff block |
| `02-architecture.md` | 2 | `ai-system-architect`: the rendered report of a schema-1.1 architecture (upstream coverage table, `INT-` interfaces, handoff block) |
| `03-workflow.md` | 3 | `ai-workflow-architect`: Full-depth workflow architecture with upstream coverage, wait limits and expiry paths, traceability |

```bash
cd examples/chain-example
S=../../skills/ai-workflow-architect/scripts
python3 $S/validate_workflow.py 03-workflow.md --strict
python3 $S/validate_ids.py 03-workflow.md
python3 $S/validate_diagrams.py 03-workflow.md
python3 $S/validate_chain.py 01-requirements.md 02-architecture.md 03-workflow.md --strict
python3 $S/generate_report.py 03-workflow.md
```

The single-skill worked examples (quick automation, AI workflow, agent, RAG, human in the loop, business process, drift review) are in `skills/ai-workflow-architect/examples/`.
