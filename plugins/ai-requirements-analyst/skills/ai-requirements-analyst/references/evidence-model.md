# Evidence Model

This is what makes V2 different from V1: every externally-derived claim carries a source, a status, and a confidence level, instead of reading as flat assertion. Read this before running any file/repository/database/API/tracker investigation.

## Evidence types

Tag the origin of every requirement or finding with one of these. Don't blend them — a requirement that mixes a user statement with an inferred detail should either be split, or have the inferred part called out separately.

| Type | Meaning |
|---|---|
| `USER_STATED` | The user told you this directly, in this conversation. |
| `DOCUMENTED` | Found in a project document, spec, README, or wiki. |
| `CODE_OBSERVED` | Found by reading source code (routes, services, models, tests). |
| `DATABASE_OBSERVED` | Found by inspecting schema/tables/relationships. |
| `API_OBSERVED` | Found in an OpenAPI/Swagger spec or API documentation. |
| `PROJECT_TRACKER_OBSERVED` | Found in a Jira/Linear/GitHub Issues/Trello item. |
| `INFERRED` | Reasoned from evidence but not directly stated anywhere — e.g. "the system likely needs an admin role because delete endpoints check `role === 'admin'`." |
| `ASSUMED` | No evidence at all; a labeled guess made to keep the analysis moving, with the reasoning and the impact if it's wrong stated alongside it. |

## Confidence model

Confidence reflects **evidence quality**, not how sure you personally feel:

- **High** — confirmed in project documentation *and* implementation (or, for a pure-conversation analysis, stated plainly and unambiguously by the user).
- **Medium** — supported by documentation but implementation not verified (or vice versa), or stated by the user but with some ambiguity remaining.
- **Low** — inferred from incomplete or indirect information.

## Attaching evidence to a requirement

Every important externally-derived requirement gets this shape (adapt fields to the output format — markdown block, table row, or JSON per `requirement-schema.md`):

```
FR-014
Requirement: Users must be able to export monthly fleet reports.
Evidence: reports.md; src/reports/export.ts; Jira issue #143
Evidence type: DOCUMENTED, CODE_OBSERVED, PROJECT_TRACKER_OBSERVED
Confidence: High
```

Do not claim a source verified something it didn't. If you read `reports.md` but never actually opened `export.ts`, don't list it as evidence — list what you actually checked.

## Implementation-status classification

When comparing documented requirements against actual implementation, classify each one:

- **Implemented** — requirement exists and implementation supports it.
- **Partially implemented** — some behavior exists but doesn't fully satisfy the requirement.
- **Not implemented** — requirement is documented but no evidence of implementation was found.
- **Implementation without documented requirement** — functionality exists but no requirement describes it. Report as *undocumented functionality*, not as a defect.
- **Conflict** — documentation and implementation disagree.

## Reporting undocumented functionality

Don't silently upgrade a discovered implementation detail into an official requirement. Report it and let a human decide:

```
Potential undocumented functionality: Password reset
Evidence: auth/reset-password module
Action: Confirm whether this behavior is an intentional requirement.
```

## Reporting contradictions

Don't decide which side (doc vs. code, or one doc vs. another) is correct — that's a business decision, not an analysis one:

```
CONFLICT-001
Documented: Admin-only deletion
Observed: Manager deletion capability (src/permissions/roles.ts)
Status: Requires business decision
```

## Missing-requirements detection

Use evidence to surface likely gaps, but don't manufacture requirements from thin signal. A gap report needs: what was found, where, and what to confirm — not an assertion that it's now a requirement.

```
Potential gap: Code contains a password-reset flow, but requirements
documentation does not mention account recovery.
Evidence: auth/reset-password module (CODE_OBSERVED)
Action: Confirm whether this should become an official requirement (FR + acceptance criteria).
```

## Privacy while gathering evidence

Avoid unnecessarily copying sensitive data into output. If a requirement can be understood from schema or metadata, don't reproduce actual customer records. Mask API keys, passwords, tokens, private credentials, and unnecessary personal data wherever they'd otherwise appear in an evidence excerpt or code snippet.
