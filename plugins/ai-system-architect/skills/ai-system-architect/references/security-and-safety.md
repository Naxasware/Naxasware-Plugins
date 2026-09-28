# Security and safety

## Architecture-level security review
Inspect evidence for authentication, authorization, secrets handling, environment variables, network boundaries, encryption, access control, sensitive-data handling. Report potential architectural concerns with evidence and confidence.
This is not a complete security audit. Say so, and do not claim audit coverage unless a dedicated security-analysis capability was actually used.

## Read-only and non-destructive
External inspection is read-only. Never delete databases, deploy to production, destroy infrastructure, modify credentials, shut down services, or run destructive migrations as part of analysis. Writes require explicit user authorization.

## Secrets and privacy
Never copy passwords, API keys, tokens or private credentials into outputs. Mask or omit them, and describe handling instead ("secret stored in environment-based secret manager"). If a secret is found in a repository, report its location and that it exists, not its value, and recommend rotation as a RECOMMENDED item. `scripts/validate_architecture.py` and `scripts/generate_report.py` catch and mask common credential patterns; they are a safety net, not a substitute for care.
