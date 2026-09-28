# Discovery playbook

## Contents
Tool selection, read-only rule, repository, dependencies, database, API, infrastructure, CI/CD, observability, failure format.

## Tool selection
Use the smallest set that answers the question.
- New system: no external tools.
- Existing repository: repository structure and search, file reading, dependency files, configuration, tests.
- Existing production architecture: add the relevant infrastructure sources.
- Database architecture: schema tools only when the user has explicitly authorized database access.
Capabilities are conceptual (inspect repository, list structure, search, read file, find symbol, inspect dependencies/configuration/tests, inspect database schema, inspect API, inspect infrastructure, search/read project items). Map them to whatever the agent actually has: shell commands, file readers, or MCP tools. Do not claim a capability the environment lacks.

## Read-only default
Repository, files, database, infrastructure, APIs, project tracker and monitoring are READ. Writes need explicit authorization and are never destructive.

## Repository (progressive)
Root files -> project type -> documentation -> configuration -> dependency files -> architecture directories -> entry points -> domain modules -> data layer -> tests. Stop as soon as the question is answered. Identify entry points, modules, layers, services, controllers, repositories, models, integrations, background jobs, events, shared libraries.

## Dependencies
Record for each notable dependency: purpose, used by, risk, recommendation. Look for circular dependencies (where detectable), unnecessary coupling, and outdated architectural assumptions.

## Database (read-only)
Inspect schema, tables, columns, indexes, relationships, constraints. Analyze entities, normalization or deliberate denormalization, observable access patterns, migration strategy. Never modify data or schema.

## APIs
Sources: OpenAPI/Swagger, GraphQL schema, gRPC definitions, discovered REST endpoints. Assess endpoints, resources, authentication, versioning, consistency, error format, pagination, rate limits, dependencies.

## Infrastructure and cloud
Where authorized: Docker, Compose, Kubernetes, Terraform, cloud configuration, environment configuration. Fill this map from evidence only: application, database, storage, queue, cache, network, secrets, monitoring, deployment. Name AWS, Azure, Google Cloud, Cloudflare, Vercel or others only when configuration shows them.

## CI/CD
GitHub Actions, GitLab CI, others. Map: build, test, security checks, artifact, deployment, environment, rollback. Report each as Observed, Missing (in what was inspected) or Unknown.

## Observability
Logging, metrics, tracing, error monitoring, health checks, alerting. Use the wording "No X configuration was found in the inspected <scope>" unless the full environment was checked.

## Project management (optional, read-only)
Issues, epics, milestones, task documentation from GitHub Issues, Jira, Linear or docs. Use to understand scope and constraints, not to modify items.

## Tool failure format
When a source cannot be reached:
```
Source:
Unavailable capability:
Impact:
What could be verified:
What remains unknown:
Alternative:
```
Never fabricate the missing evidence. If everything is unavailable, fall back to design from requirements.
