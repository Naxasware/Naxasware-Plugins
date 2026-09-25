# Tool Architecture

V2's job is to inspect the actual environment, not only what the user manually describes — but through narrowly scoped, read-first tools, never one giant "analyze everything" call. Which of these are actually available depends on what's connected in a given session; check before assuming any category is usable.

## Tool categories

### File tools
`list_project_files`, `read_project_file`, `search_project_files`, `extract_document_structure`. Use for requirements docs, specs, spreadsheets, PDFs, project notes — anything sitting in the user's files.

### Repository tools
`inspect_repository`, `list_repository_structure`, `search_repository`, `read_repository_file`, `inspect_issues`, `inspect_pull_requests`, `inspect_project_documentation`. Purpose: understand the existing implementation before proposing requirements that conflict with it. When investigating a repo, prioritize in roughly this order of signal-to-noise: README → docs → routes/controllers/services → models/schema → configuration → tests → frontend screens → API definitions. Use targeted search, not a blind full-repo read.

### Database tools
`inspect_database_schema`, `list_tables`, `describe_table`, `inspect_relationships`. Optional and permission-controlled. **Read-only, always** — never modify a production database, and never run this category without it being explicitly authorized/connected for the session.

### API tools
`inspect_api_definition`, `read_openapi_spec`, `list_api_endpoints`, `inspect_endpoint_schema`. Inputs: OpenAPI/Swagger specs, API documentation.

### Project management tools
Jira, Linear, GitHub Issues, Trello, or similar: `list_project_requirements`, `read_issue`, `search_issues`, `inspect_epics`, `inspect_tasks`. Read-only by default.

### CRM / business-system tools
`inspect_customer_fields`, `inspect_workflow`, `inspect_business_process`. Optional — only use when the integration is explicitly authorized for this session; don't assume availability.

## Permission model

**Read before write.** V2 is primarily a read/analyze system.

| Category | Default |
|---|---|
| Files | READ |
| Repository | READ |
| Database | READ |
| API definitions | READ |
| Project management | READ |
| CRM | READ |
| External mutation (any write, comment, ticket creation, email/message send) | DISABLED |

Any write operation requires explicit, separate authorization from the user and is never implied by a request to "analyze," "compare," "audit," or "investigate." If a user's request seems to call for a write (e.g. "file a ticket for this gap"), treat that as a distinct follow-up action to confirm, not a step inside the requirements-analysis workflow.

## Tool selection rules

Don't call every available tool for every task — use the smallest set the question actually needs.

| Request | Tools to use |
|---|---|
| "Turn this idea into requirements." | None. |
| "Analyze the requirements in this repository." | Repository/file tools. |
| "Compare our requirements with our current implementation." | Requirements source + repository. |
| "Analyze our database requirements." | Database schema inspection — only if authorized. |
| "What does our API currently expose?" | API tools (OpenAPI/Swagger spec or docs). |
| "What's in our backlog for this feature?" | Project management tools, read-only. |

If a category isn't connected/authorized, don't stall the whole analysis waiting for it — proceed with what is available and note in Failure Handling (in SKILL.md) what couldn't be checked.

## AI-system requirements (when the project itself contains AI)

When repository/documentation evidence shows models, prompts, agents, tool integrations, RAG, vector databases, evaluations, guardrails, human-approval steps, or training/inference data sources, capture each as: Input, Context, Tool access, Expected output, Evaluation approach, Failure behavior, Human oversight, Data/privacy concerns, Cost considerations. Don't introduce an "AI Requirements" or "Automation Requirements" section just because the project is AI-adjacent — only include it when there's real evidence or a stated objective it serves (this rule carries over from V1: see `SKILL.md`'s "don't invent" discipline).

## Workflow discovery

Where workflow definitions exist (state machines, orchestration configs, BPMN-like docs), reconstruct as: Trigger → Condition → Action → Integration → Result → Failure. Only reconstruct workflows evidence actually supports.

## Security-relevant evidence

While investigating, note evidence of: authentication, authorization, roles, secrets handling, personal data, financial data, audit logs, encryption, session management — these feed non-functional and business-rule requirements. This is passive observation for requirements purposes only; **never** perform offensive security testing (attempting exploits, probing for vulnerabilities) as part of this work.
