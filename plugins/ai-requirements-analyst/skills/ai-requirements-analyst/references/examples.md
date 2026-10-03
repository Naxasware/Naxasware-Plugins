# Worked Example

Input from the user (Requirements Extraction mode — they described a business problem):

> "Our company tracks vehicle maintenance manually and often misses service dates."

## How this gets worked through

**Problem statement.** Vehicle maintenance is tracked manually (method not specified — likely spreadsheet or paper), and service dates are being missed. Impact of missed service dates (cost, downtime, safety, compliance) wasn't stated — that's worth a targeted question if it changes urgency/scope, otherwise note as unknown.

**Business objective (BO-001).** Reduce or eliminate missed vehicle maintenance by replacing manual tracking with a system that proactively surfaces when service is due.

**Stakeholders / Actors.** Fleet Administrator is a safe inference (someone manages the vehicles today, even manually) — but the specific role name, and whether there's also a Driver or Manager actor, wasn't stated. Note Fleet Administrator as a reasonable working actor, and flag "who else touches this process?" as an open question rather than inventing a full cast of roles.

**Current state (AS-IS).** Only what's actually supported: tracking is manual; service dates are sometimes missed. Resist the pull to also assert "probably uses a spreadsheet with no reminders" — that's plausible but unconfirmed; if it matters, ask.

**Future state (TO-BE), sketched at a high level.** Vehicle records with mileage/date tracking → system calculates maintenance due status against a configured interval → surfaces due/overdue vehicles.

**A first functional requirement:**

```
FR-001 — Create Vehicle
Actor: Fleet Administrator
Trigger: Administrator selects "Add Vehicle"
Precondition: Administrator is authenticated.
Behavior: System allows the administrator to enter vehicle information.
Required data: Registration number, Make, Model, Year, Current mileage, Assigned department
Acceptance: A valid vehicle record is created and receives a unique identifier.
```

**A business rule inferred from the stated need, not invented:**

```
BR-002: Preventive maintenance becomes due after the configured mileage interval or date interval, whichever occurs first.
```
(This is a reasonable operationalization of "misses service dates" — flag it as something to confirm, since "mileage OR date, whichever first" is one common pattern but not the only one; ask if unsure rather than asserting it as fact.)

**Acceptance criterion:**

```
Given a vehicle has 9,900 km since its last service,
When the administrator records 10,000 km,
Then the system marks the configured maintenance interval as due.
```

**Assumptions (A-xxx), not folded into the requirements:**
- A-001: Maintenance intervals are configurable per vehicle type rather than global. *Reason:* different vehicle types typically have different service schedules. *Impact if wrong:* data model needs a single global interval instead of per-type. *Needs confirmation: yes.*

**Open questions (Q-xxx), kept short:**
- Q-001: Should the system notify someone when a vehicle becomes due, or is a dashboard/list sufficient for v1?
- Q-002: Is there more than one actor role involved (e.g., drivers logging mileage themselves vs. an administrator doing it centrally)?

**What this is not.** No NFR section was fabricated ("the system should be secure and scalable") — with nothing said about expected fleet size, user count, or compliance context, those would be guesses. If the user's next message gives that context, add it then.

## The pattern to take away

Notice what happened here: a two-sentence problem statement produced a real first pass at FR/BR/AC — but every place the input ran out, the response either asked (Q-001, Q-002) or clearly flagged a guess (A-001, the "whichever first" business rule) instead of quietly deciding it. That's the whole discipline in miniature.

## A V2 worked example (repository connected)

Input:

> "Analyze our existing fleet management system and tell me what requirements we actually have."

**Tool selection.** Requirements-vs-Implementation Comparison / Existing-System Reconstruction — repository and file tools, read-only. No database or API tools needed unless the repo points to them and the question requires it.

**Discovery path taken.** README → existing docs → routes → models → workflows → tests, per `tool-architecture.md`.

**A reconstructed requirement, evidence-backed:**

```
FR-001 — Record vehicle mileage
Actor: ACT-002 Driver (observed role check in src/vehicles/mileage.ts)
Evidence: src/vehicles/mileage.ts
Evidence type: CODE_OBSERVED
Status: Implemented
Confidence: High
```

**Undocumented functionality, reported rather than silently added as a requirement:**

```
FR-CANDIDATE-001 — Maintenance reminders
Evidence: src/maintenance/reminders.ts
Evidence type: CODE_OBSERVED
Status: Observed in implementation but not documented.
Action: Confirm whether this should become an official requirement.
```

**What didn't happen:** the analysis didn't claim GitHub Issues showed anything, because the issue tracker wasn't connected this session — that limitation was stated plainly (per Failure Handling in `SKILL.md`) rather than glossed over. It also didn't attempt to modify the repository, run tests, or comment on any issue — read-only the whole way through, per the permission model in `tool-architecture.md`.
