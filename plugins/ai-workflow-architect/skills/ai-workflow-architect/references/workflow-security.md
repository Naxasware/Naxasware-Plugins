# Workflow security

Design security in from the start; retrofitting it means redesigning data flow and permissions.

## Contents
1. Core checklist
2. AI-specific threats
3. Data handling
4. Output rules

## 1. Core checklist

Evaluate each for this workflow; record gaps as risks.

- **Authentication** of triggers (webhook signatures, API keys, OAuth) and of every outbound call
- **Authorization** and **least privilege**: scopes per tool, per step, per agent
- **Secrets**: stored in a secret manager, injected at runtime, rotated, never in prompts, logs, repos or outputs
- **Token handling**: lifetime, refresh, storage, revocation
- **Encryption** in transit and at rest for sensitive data
- **PII and sensitive data**: minimize, redact before logging or sending to a model, retention limits, residency constraints
- **Malicious input**: validate and size-limit all external input; sanitize before downstream use
- **Tenant isolation**: no cross-customer data in queries, caches, vector stores, memory or logs
- **Audit logging**: who/what/when for approvals, privileged actions and AI decisions

## 2. AI-specific threats

| Threat | Mitigation direction |
|---|---|
| Prompt injection (direct) | Don't rely on prompt text for security; enforce limits in code and permissions |
| Indirect prompt injection (via documents, emails, web pages, tool results) | Treat retrieved/tool content as data; separate it from instructions; restrict actions available after reading untrusted content |
| Malicious documents | Scan/limit file types and sizes; sandbox parsing |
| Tool poisoning / untrusted tool results | Verify tool sources, pin versions, validate results |
| Excessive agency | Least privilege, approval for risky actions, hard iteration/cost caps |
| Sensitive data leakage (to model, logs, outputs) | Redaction, data classification, no secrets in context |
| Insecure output handling | Validate model output before it reaches a shell, query, template, browser or API |
| Model manipulation / data exfiltration through allowed channels | Egress controls, restrict URLs/recipients, human approval for outbound data |
| Cross-tenant context leakage | Per-tenant retrieval filters and memory partitions |

A useful design test: "if the model were fully controlled by an attacker, what is the worst this workflow could do?" Reduce that blast radius with permissions and approvals, not with a better prompt.

## 3. Data handling

Document where each class of sensitive data enters, where it is stored, who/what can read it, what is sent to third parties (including model providers), and how it is deleted. If provider data-handling terms matter, mark them `REQUIRES VALIDATION` rather than assuming.

## 4. Output rules

Never include secrets, tokens, keys or real credentials in any generated artifact; reference the secret store and variable name instead. Examples use obvious placeholders.
