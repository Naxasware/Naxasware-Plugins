# Examples

Sample inputs and outputs, used both as documentation and as smoke-test fixtures for the bundled scripts.

| File | What it is | Try it with |
|---|---|---|
| `sample-architecture.json` | A fictional architecture-review output (multi-tenant SaaS) conforming to `references/output-schema.md` — evidence, components, a decision, a risk, and traceability all populated. | `python3 ../skills/ai-system-architect/scripts/validate_architecture.py sample-architecture.json` |
| `sample-diagram.mmd` | A Mermaid flowchart whose node names match `sample-architecture.json`'s components — shows the diagram-consistency check passing. | `python3 ../skills/ai-system-architect/scripts/validate_diagrams.py sample-architecture.json sample-diagram.mmd` |

Run both in sequence to sanity-check a fresh install, then render the report:

```bash
cd examples
python3 ../skills/ai-system-architect/scripts/validate_architecture.py sample-architecture.json
python3 ../skills/ai-system-architect/scripts/validate_diagrams.py sample-architecture.json sample-diagram.mmd
python3 ../skills/ai-system-architect/scripts/generate_report.py sample-architecture.json
```

All should exit cleanly with no errors.

## Chain example

`chain-example/` is a complete stage-2 example that follows a stage-1 requirements document:

| File | What it is |
|---|---|
| `01-requirements.md` | The upstream requirements document (from `ai-requirements-analyst`). |
| `02-architecture.json` | Schema 1.1 architecture with `project.chain`, `upstream_coverage`, `carried_forward`, `handoff`, `INT-` interfaces and `A-` / `Q-` items that continue the upstream numbering. |
| `02-architecture.md` | `generate_report.py` output for the JSON above: chain header, coverage table and handoff block included. |
| `02-diagram.mmd` | Mermaid diagram whose nodes match the components. |

```bash
cd examples/chain-example
python3 ../../skills/ai-system-architect/scripts/validate_architecture.py 02-architecture.json --upstream 01-requirements.md --strict
python3 ../../skills/ai-system-architect/scripts/validate_diagrams.py 02-architecture.json 02-diagram.mmd
python3 ../../skills/ai-system-architect/scripts/validate_chain.py 01-requirements.md 02-architecture.md
```
