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
