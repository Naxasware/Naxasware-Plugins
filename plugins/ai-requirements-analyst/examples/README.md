# Examples

Sample inputs and outputs, used both as documentation and as smoke-test fixtures for the bundled scripts.

| File | What it is | Try it with |
|---|---|---|
| `sample-discovery-report.md` | A Discovery Report produced from a two-sentence app idea, with no tools — shows the offline/V1 path (labeled assumptions and open questions, no invented facts). | `python3 ../skills/ai-requirements-analyst/scripts/validate_ids.py sample-discovery-report.md` |
| `sample-audit-input.md` | A small requirements doc with a deliberately planted contradiction and vague ("fast and secure") language — feed this to the skill and ask for an audit to see the Analysis/Audit mode in action. | `python3 ../skills/ai-requirements-analyst/scripts/validate_ids.py sample-audit-input.md` |
| `sample-evidence-comparison.md` | A Requirements-vs-Implementation Comparison output, evidence-tagged, showing a Conflict, a Partially-implemented requirement, and an Undocumented-functionality finding. | `python3 ../skills/ai-requirements-analyst/scripts/validate_requirements.py sample-evidence-comparison.md` |
| `chain-example/01-requirements.md` | A chain-ready requirements document (chain header, evidence labels, a client conflict kept open as CONFLICT-001, acceptance criteria for every FR, handoff block) with the brief it came from. Stages 2 and 3 of the same example live in the other two plugins. | `python3 ../skills/ai-requirements-analyst/scripts/validate_ids.py chain-example/01-requirements.md --strict` |
| `sample-requirements.json` | Structured JSON conforming to the schema in `references/requirement-schema.md` — feed this to `generate_report.py` to see all three export formats. | `python3 ../skills/ai-requirements-analyst/scripts/generate_report.py sample-requirements.json --format markdown` |

Run all four in sequence to sanity-check a fresh install:

```bash
cd examples
python3 ../skills/ai-requirements-analyst/scripts/validate_ids.py sample-discovery-report.md
python3 ../skills/ai-requirements-analyst/scripts/validate_ids.py sample-audit-input.md
python3 ../skills/ai-requirements-analyst/scripts/validate_requirements.py sample-evidence-comparison.md
python3 ../skills/ai-requirements-analyst/scripts/generate_report.py sample-requirements.json --format markdown
python3 ../skills/ai-requirements-analyst/scripts/generate_report.py sample-requirements.json --format csv
python3 ../skills/ai-requirements-analyst/scripts/generate_report.py sample-requirements.json --format matrix
```

All should exit cleanly with no errors.
