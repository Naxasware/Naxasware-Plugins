# Structured output schema (version 1.1)

Produce JSON only when the user wants machine-readable output. Validate with `scripts/validate_architecture.py`. Set `project.schema_version` to `"1.1"` (1.0 files still validate); bump it when the shape changes.

## Top-level sections
Objects: `project`, `business_context`, `selected_architecture`, `data_architecture`, `api_architecture`, `integration_architecture`, `security_architecture`, `infrastructure`, `deployment`, `observability`, `ai_architecture`.
Arrays: `architecture_drivers`, `constraints`, `quality_attributes`, `architecture_options`, `components`, `modules`, `decisions`, `risks`, `assumptions`, `open_questions`, `evidence`, `traceability`.
Use `{}` or `[]` for sections that do not apply; do not omit them.

## Item shapes (checked by the validator)
- evidence: `id`, `types` (list from the 12 evidence types), `sources` (required for observed or documented types), `confidence` (High, Medium, Low, Unknown), `note`.
- components: `id`, `name`, `origin` (observed = seen by inspection; stated = the user or a document says it exists, cite a USER_STATED or DOCUMENTED evidence id; recommended; assumed; unknown), `evidence_ids` (required when observed), optional `classification`, `responsibility`, `diagram_exempt`.
- decisions: `id`, `title`, `classification` (REQUIRED, RECOMMENDED, OPTIONAL, FUTURE, EXPERIMENTAL), optional `driver`, `components`, `confidence`.
- risks: `id`, `risk`, `evidence`, `impact`, `likelihood`, `mitigation`, `contingency`, `affected_component`.
- quality_attributes: `status` if present is Covered, Partially Covered, Not Covered or Unknown.
- traceability: `requirement`, `driver`, `decision`, `component`.
- Unique `id` per array. No numeric `score`/`rating` fields. No secret values.

See `examples/sample-architecture.json` in the plugin root for a complete fictional example.

## Schema 1.1: chain and traceability additions
Used when this architecture follows `ai-requirements-analyst` and feeds `ai-workflow-architect` (see `chaining.md`). All are optional outside a chain.
- `project.chain`: `{"stage": 2, "skill": "ai-system-architect", "upstream": ["01-requirements.md"], "next": "ai-workflow-architect"}`. `generate_report.py` writes it as the `> Chain:` header on the first line.
- `upstream_coverage`: one entry per upstream FR, NFR, BR, AIR, IR, CON and DEP: `{"upstream": "FR-004", "handled_by": "COMP-003, ADR-004", "status": "Covered | Partially covered | Deferred | Out of scope", "reason": "..."}`. A reason is required for Deferred and Out of scope. Ranges such as `"FR-001 to FR-004"` are allowed.
- `carried_forward`: how upstream assumptions and open questions stand, for example `{"assumptions": "A-001 to A-005 still hold", "questions": "Q-003 and Q-004 still open and blocking"}`.
- `handoff`: `{"next_skill": "...", "must_cover": [...], "locked_decisions": [...], "blocking_questions": [...], "next_a": "008", "next_q": "011"}`. Write the next numbers as plain digits, not as `A-008`.
- `assumptions` and `open_questions` items may be objects `{"id": "A-006", "text": "..."}` / `{"id": "Q-007", "text": "...", "why": "..."}`. In a chain, new numbers continue after the highest upstream A- and Q-.
- `integration_architecture.interfaces`: list of `{"id": "INT-001", "name": "...", "status": "...", "note": "..."}`. Do not use `INT-001` as an object key.
- `constraints`: in a chain, cite an upstream `CON-nnn` instead of restating it: give your own constraint an id such as `CST-001` and put the upstream id in `"cites": ["CON-001"]`.
- IDs owned by stage 1 (`BO ST ACT FR NFR BR DR IR AIR AR UC US AC CON DEP`) are cited, never defined here. This stage defines `AD ADR RISK DEBT INT EVT COMP`.

Check with `python3 scripts/validate_architecture.py architecture.json --upstream 01-requirements.md --strict`, then render with `scripts/generate_report.py architecture.json -o 02-architecture.md`.
