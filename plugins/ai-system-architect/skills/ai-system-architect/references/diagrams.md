# Diagrams

Formats: Mermaid (default), PlantUML, ASCII, structured JSON.
Types: system context, container, component, sequence, deployment, data flow, AI architecture, network, event flow, authentication flow. Draw only what helps the decision at hand.

## Consistency rules
- Every diagram component exists in the architecture specification, and every architecture component appears in at least one diagram unless marked `"diagram_exempt": true`.
- Use the component names (or IDs) from the architecture exactly, so they can be checked.
- Show observed and recommended elements distinguishably (for example a `%% recommended` comment or a dashed style) when both appear.
- Flag "Diagram contains undocumented component" and "Architecture contains component missing from diagram" when found.

## Mermaid example
```
flowchart LR
  WEB[Web App] -->|HTTPS| API[API Service]
  API --> TCL[Tenant Context Layer]
  TCL --> DB[(PostgreSQL)]
```
Check with: `python3 scripts/validate_diagrams.py architecture.json diagram.mmd`.
