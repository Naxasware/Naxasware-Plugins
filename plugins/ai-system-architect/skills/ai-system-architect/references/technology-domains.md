# Technology Domains

Read whichever sections below the project actually touches — not every project needs all of them. Each section is a lens for analysis, not a checklist that must be filled regardless of relevance.

## Frontend architecture

Where a frontend is in scope, define: the application shape, routing, state management, API communication pattern, authentication/authorization handling, component organization, caching, error handling, accessibility, performance, and responsive behavior. Don't prescribe a specific framework without a stated reason (team familiarity, an SSR requirement, a specific ecosystem need) — "React because it's popular" fails the requirements-before-technology principle just as much as a backend choice would.

## Backend architecture

Define the application layer, domain/business logic, services, repositories, API layer, validation, authN/authZ, background jobs, event handling, and error handling. A common layering to consider, when it fits the project's complexity:

```
Controller → Application Service → Domain Logic → Repository → Database
```

Don't impose this layering on a genuinely simple CRUD system where it would just add indirection with no corresponding benefit.

## Database architecture

**Type** — relational, document, key-value, graph, time-series, search, vector. **Selection criteria** — consistency needs, query patterns, transaction requirements, scale, relationship complexity, cost, operational complexity. Choose based on which of these the project's data actually has, not on which database is currently fashionable; a relational database handling a modest CRUD workload doesn't need to become a document store because a document store scales well for use cases this project doesn't have.

## Data architecture

Define major entities, their relationships, who owns each entity, its lifecycle, consistency requirements, retention policy, archival approach, backup approach, deletion handling, and migration strategy. Data ownership questions ("who is allowed to be the source of truth for this field") surface real architectural decisions that a pure ER diagram hides.

## API architecture

Define API style, endpoint organization, authentication, authorization, validation, versioning, pagination, filtering, rate limiting, error response format, idempotency, and documentation approach. Styles to choose among: REST, GraphQL, gRPC, event-based APIs, internal service APIs — justified by client needs and integration patterns, not by convention.

## Integration architecture

For every major external integration:

```
Integration ID (INT-001...)
External system
Purpose
Protocol
Direction        inbound / outbound / bidirectional
Data exchanged
Authentication
Trigger           what causes this integration to fire
Frequency
Timeout
Retry behavior
Failure handling
Monitoring
```

## Event architecture

When the system is event-driven (justify this against the anti-patterns list before assuming it), define per event type:

```
Event (EVT-001...)
Producer
Consumer(s)
Payload
Delivery guarantee
Ordering requirement
Retry behavior
Dead-letter behavior
Idempotency handling
Observability
```

## Authentication architecture

Analyze: authentication method, session/token strategy, identity provider (build vs. third-party), password handling, MFA, session expiration, refresh tokens, account recovery. Only include advanced mechanisms (hardware keys, adaptive MFA, federated SSO) when a stated requirement — compliance, enterprise customer demand, risk profile — actually calls for them.

## Authorization architecture

Define roles, permissions, resource-level access, organization-level access, tenant isolation (if multi-tenant), and administrative privilege boundaries. Approaches: RBAC, ABAC, policy-based authorization — pick based on how granular and how dynamic the permission model actually needs to be; RBAC is usually sufficient and ABAC/policy engines are justified by genuinely dynamic, attribute-dependent rules.

## Security architecture

- **Application security** — input validation, output encoding, secure authentication, authorization enforcement, secrets management, dependency management
- **Data security** — encryption (at rest / in transit), key management, data classification, retention
- **Infrastructure security** — network boundaries, firewalling, IAM, environment separation
- **Operational security** — logging, auditing, monitoring, incident response

This skill produces architecture-level security recommendations — it is not a penetration test and shouldn't be presented as one.

## Multi-tenant / SaaS architecture

Evaluate tenant isolation model: shared database, shared schema, separate schema, separate database, or hybrid — trade off operational simplicity against isolation guarantees and per-tenant customization needs. Also analyze: tenant identification (how a request resolves to a tenant), authorization within tenant boundaries, data-leakage risk, per-tenant scaling, migration strategy across all tenants, backup strategy, and tenant-specific configuration.

## Caching architecture

Where caching is justified: cache location (client, CDN, application, database), cache key design, TTL, invalidation strategy, consistency implications, and fallback behavior when the cache is unavailable or cold.

## File storage architecture

Where files are involved: object storage choice, upload flow, validation, size limits, access control, signed URLs, malware/virus scanning where the content justifies it, retention, and deletion handling.

## Background processing

Identify work that shouldn't block a synchronous request — email, report generation, file processing, AI jobs, notifications, data imports, scheduled tasks — and define the queue, worker model, retry policy, failure handling, dead-letter behavior, and monitoring for each.

## Search architecture

When search is a real requirement (not just "users might want to filter a list," which a database query usually covers): evaluate database-native search vs. full-text search vs. a dedicated search engine, and define indexing strategy, ranking, filtering, and how the index stays in sync with the source of truth.
