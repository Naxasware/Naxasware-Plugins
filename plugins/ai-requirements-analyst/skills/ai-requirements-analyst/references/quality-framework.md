# Quality Framework

## The seven-point check

Run this over every major requirement before calling a spec finished, and run it explicitly (findings, not just a silent pass) when the mode is a Requirements Analysis / Audit:

1. **Clarity** — could a developer implement this without asking what it means?
2. **Completeness** — is something important obviously missing (a precondition, an actor, an error case)?
3. **Consistency** — does it contradict another requirement elsewhere in the doc?
4. **Testability** — could someone write a test or acceptance check for this as written?
5. **Traceability** — does it connect back to a real business objective, or is it there for its own sake?
6. **Feasibility** — is it realistic given the stated constraints (budget, timeline, tech)?
7. **Scope** — does it actually belong in this project, or has scope quietly crept?

## Ambiguity detection

Watch for words that sound like requirements but aren't measurable: *fast, easy, secure, user-friendly, automatic, real-time, scalable, advanced, intelligent, flexible, efficient.* When one of these affects implementation (most of the time it will), do one of two things — ask for the measurable version, or clearly label the gap:

- Instead of "The system should be fast," write "Response-time target is not yet defined" (and, if it matters enough, add it as an open question).
- Instead of silently interpreting "secure" as some specific auth scheme, ask what "secure" needs to mean here (compliance requirement? just login-gated? encrypted at rest?) or flag it as unresolved.

## Running a Requirements Analysis / Audit (mode 3)

When the user hands you an existing document (or set of notes that already function as one) and wants it reviewed:

1. Read the whole thing before critiquing any of it.
2. Walk the seven-point check across the document as a whole and, where useful, per major requirement.
3. Specifically hunt for: missing roles, missing permissions, missing NFR categories, missing edge cases, requirements that contradict each other, and vague/adjective-laden requirements that ambiguity detection should have caught.
4. Present findings as findings — "here's what's solid, here's what's missing or unclear, here's what contradicts what" — rather than silently rewriting their document into your own version. If they then ask you to fix it, that's a separate step.
5. Don't manufacture problems to seem thorough. If a section is genuinely fine, say so briefly and move on.

## Prioritization

Use MoWSCoW as a practical framework, not gospel: **Must Have / Should Have / Could Have / Won't Have Now.**

For MVP Definition specifically: the bar for "Must Have" is "the core business objective doesn't work without this," not "this is quick to build." Something can be trivial to implement and still be a Could Have, and something can be effortful and still be a Must Have if the product doesn't function without it.

## Auditing with evidence (V2)

When a repository or other system is connected, the audit above gets an extra axis: for each documented requirement, check whether tool-derived evidence *supports*, *partially supports*, *contradicts*, or *says nothing about* it, using the classification in `evidence-model.md`. Report that alongside the seven-point check rather than as a separate disconnected pass — a requirement can be perfectly clear and testable on paper and still be Not Implemented, and both facts matter to the reader.

## Assumption vs. requirement

An assumption is something you filled in because it wasn't stated, and the spec would still function (just possibly differently) if it turns out to be wrong. A requirement is something the user told you or a document confirms. Keep these typographically and structurally distinct (separate section, separate ID prefix — A-xxx vs the requirement prefixes) so nobody downstream mistakes a guess for a fact.
