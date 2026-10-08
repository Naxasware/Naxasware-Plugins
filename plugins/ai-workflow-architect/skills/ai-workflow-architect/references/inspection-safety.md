# Inspection safety, tool failures and offline mode

## Contents
1. Read-only by default
2. Secrets and sensitive data
3. Tool safety card
4. Tool failure handling
5. Offline mode
6. Portability and adapters

## 1. Read-only by default

External inspection is read-only. Without explicit, separate permission from the user do not: delete data, modify production databases, deploy, destroy infrastructure, rotate credentials, shut services down, run migrations, modify or activate workflows, send external messages, or run financial transactions. If a diagnosis needs a write (re-run a failed execution, toggle a flag), describe it as a recommended action and let the owner do it. Any future write capability must be designed and permissioned on its own.

Also follow least privilege: ask for or use the narrowest access that answers the question, and stop if a tool would exceed it.

## 2. Secrets and sensitive data

- Never reveal passwords, API keys, OAuth tokens or private keys found in files, configuration, prompts, logs or databases. Mask them: `API_KEY=********`.
- Refer to credentials by name or secret-store path only.
- Retrieve the minimum data needed; prefer schemas and aggregates over rows; do not copy personal data into reports.
- If you find an exposed secret, report the location and type (masked), recommend rotation by the owner, and do not repeat the value.
- Respect permission boundaries; a tool that returns more than you asked for is still bound by these rules.

## 3. Tool safety card

Before relying on an external tool, state (or ask the environment for) this, and write it in the report for anything the design depends on:

```text
Tool Name | Purpose | Read/Write | Permissions | Inputs | Outputs | Side Effects
Risk | Authentication | Rate Limits | Failure Modes
```

Anything not known is `UNKNOWN` or `REQUIRES VALIDATION`. A tool whose write behavior is unknown is treated as write-capable.

## 4. Tool failure handling

When a tool fails or is unavailable, record:

```text
Capability | Status | What Was Verified | What Was Not Verified | Reason | Fallback | Impact
```

Then continue with the evidence you have, list what stays unknown and how that limits each conclusion, and deliver the architecture with its limitations stated. Never fill the gap with plausible detail: missing evidence stays missing.

## 5. Offline mode

With no external tools the plugin works as the V1 method on what the user supplied or described: requirements, architecture, diagrams, trade-offs, risks, implementation plan and validation. Label everything `USER_STATED`, `DOCUMENTED`, `ASSUMED` or `RECOMMENDED`; there is no observed layer, so do not produce drift records, only a list of checks to run once access exists.

## 6. Portability and adapters

The method is platform-neutral and lives in `SKILL.md` and `references/`. Tool access is an adapter concern: use the environment's own repository, workflow, database, API, infrastructure, monitoring and tracker tools and its own names for them. Claude and Claude Code are the default environment but not a requirement. Where skill discovery, MCP or inspection tools are missing, `SKILL.md` plus `references/` and `examples/` is the complete fallback.
