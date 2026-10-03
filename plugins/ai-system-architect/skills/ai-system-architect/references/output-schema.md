# Structured output schema (version 1.0)

Produce JSON only when the user wants machine-readable output. Validate with `scripts/validate_architecture.py`. Set `project.schema_version` to `"1.0"`; bump it when the shape changes.

## Top-level sections
Objects: `project`, `business_context`, `selected_architecture`, `data_architecture`, `api_architecture`, `integration_architecture`, `security_architecture`, `infrastructure`, `deployment`, `observability`, `ai_architecture`.
Arrays: `architecture_drivers`, `constraints`, `quality_attributes`, `architecture_options`, `components`, `modules`, `decisions`, `risks`, `assumptions`, `open_questions`, `evidence`, `traceability`.
Use `{}` or `[]` for sections that do not apply; do not omit them.

## Item shapes (checked by the validator)
- evidence: `id`, `types` (list from the 12 evidence types), `sources` (required for observed or documented types), `confidence` (High, Medium, Low, Unknown), `note`.
- components: `id`, `name`, `origin` (observed, recommended, assumed, unknown), `evidence_ids` (required when observed), optional `classification`, `responsibility`, `diagram_exempt`.
- decisions: `id`, `title`, `classification` (REQUIRED, RECOMMENDED, OPTIONAL, FUTURE, EXPERIMENTAL), optional `driver`, `components`, `confidence`.
- risks: `id`, `risk`, `evidence`, `impact`, `likelihood`, `mitigation`, `contingency`, `affected_component`.
- quality_attributes: `status` if present is Covered, Partially Covered, Not Covered or Unknown.
- traceability: `requirement`, `driver`, `decision`, `component`.
- Unique `id` per array. No numeric `score`/`rating` fields. No secret values.

See `examples/sample-architecture.json` in the plugin root for a complete fictional example.
