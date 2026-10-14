# Operations Architecture

Read this before writing the infrastructure/operations sections of a Full or Standard-package output.

## Deployment architecture

```
Developer environment → CI/CD → Staging → Production
```

Where relevant, define: frontend hosting, application servers, databases, object storage, queues, CDN, load balancing, secrets management, and monitoring — only for the pieces the architecture actually has.

## Cloud architecture

Evaluate AWS, Azure, Google Cloud, Cloudflare, Vercel, other suitable platforms, self-hosting, or hybrid infrastructure — never default to one provider without comparing against the project's actual needs. Compare on: requirements fit, cost, team's existing expertise, available managed services, portability (how locked-in the choice makes the team), operational complexity, and geographic requirements.

## DevOps architecture

Analyze: source control and branching strategy, CI, CD, testing strategy, deployment approach, rollback strategy, infrastructure as code, secrets handling, environment separation, and observability tooling.

## Observability architecture

- **Logs** — what should be logged, and at what level, so an incident is debuggable after the fact
- **Metrics** — what should be measured to know the system is healthy
- **Traces** — where distributed tracing actually earns its complexity (multi-service request paths)
- **Alerts** — what conditions require someone to be paged or notified
- **Audit** — what user/system actions need an immutable audit record (often driven by a compliance requirement)

## Reliability architecture

Consider: redundancy, retries, timeouts, circuit breakers, graceful degradation, health checks, backups, and disaster recovery — proportional to the availability requirement actually stated, not maximal by default.

## Backup and disaster recovery

```
Backup frequency
Retention period
Recovery Point Objective (RPO)
Recovery Time Objective (RTO)
Restore process
Disaster scenarios considered
Failover strategy
```

Never invent RPO/RTO values — ask for them, or provide an explicitly labeled planning assumption ("Assumption: RPO of 24h, revisit once a business owner confirms an acceptable data-loss window").

## Performance architecture

Identify latency targets, throughput requirements, likely bottlenecks, where caching helps, where asynchronous processing removes work from the critical path, database optimization needs, CDN usage, and frontend performance concerns. State performance targets as measurable numbers where the input supports it; otherwise flag them as undefined rather than writing "the system should be fast."

## Scalability architecture

Consider, each only as far as justified by the scale model: vertical scaling, horizontal scaling, database scaling (read replicas, connection pooling), stateless service design (a prerequisite for most horizontal scaling), queue-based load leveling, caching, and partitioning/sharding. Partitioning and sharding in particular carry enough operational cost that they need a real scale driver behind them, not just "we might get big."

## Cost architecture

Provide a cost *model* — the categories that drive spend — rather than fabricated dollar figures when exact current pricing isn't known:

```
Compute
Database
Storage
Bandwidth
Third-party APIs
AI/model usage
Monitoring
Email/SMS
Development/operations overhead
```

If precise numbers matter to the user, say that current pricing should be checked against the relevant provider rather than presenting an invented figure as accurate.
