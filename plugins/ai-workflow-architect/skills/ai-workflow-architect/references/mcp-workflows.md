# MCP in workflows

MCP (Model Context Protocol) is an optional mechanism for giving models standardized access to tools, resources and prompts. Treat it as an architectural choice that must earn its place.

## Use MCP when
- Several models/agents/clients need the **same** tool or context surface and a standard interface avoids per-client glue
- You want discoverable, self-describing tools with a uniform auth and audit story
- A suitable MCP server already exists and has been verified

## Don't use MCP when
- The workflow is deterministic code calling a few known APIs — call them directly
- The only reason is "the workflow contains AI"
- You'd be adding a server to operate, secure and version for a single caller

## What to define if you use it
- **Server** — who builds/hosts/owns it; transport; versioning
- **Tools** — each as a `TOOL-` entry (see `tool-architecture.md`)
- **Resources and prompts** — what is exposed read-only vs actionable
- **Authentication and permissions** — per-user vs shared credentials; scopes; least privilege
- **Data boundaries** — what may flow back to the model; redaction; tenant isolation
- **Failure behavior** — timeouts, server unavailable, partial results
- **Tool discovery** — which tools a given agent may see (don't expose everything by default)
- **Auditability** — log every call with caller, arguments, result status

## Security notes
Tool descriptions and results come from a server you may not control; treat them as untrusted input (tool poisoning, indirect prompt injection). Pin and review server versions; prefer servers you operate for sensitive data. Never assume a third-party server's capabilities or safety without verification (`REQUIRES VALIDATION`). See `workflow-security.md`.
