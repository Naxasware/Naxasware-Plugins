# Reliability: errors, retries, idempotency, timeouts, human-in-the-loop, state

Reliability is a first-class requirement. For every step with an external effect, the architecture must answer the questions below. This file is the checklist.

## Contents
1. Error categories
2. Retry architecture
3. Idempotency
4. Timeouts
5. Partial failure and recovery
6. Human-in-the-loop
6b. Waiting on an external party
7. State and resumption
8. Per-step reliability checklist

## 1. Error categories

| Category | Examples | Typical handling |
|---|---|---|
| Input | Missing/invalid payload, wrong type, oversized file | Validate at the edge; reject or quarantine; don't retry |
| Tool/API | 5xx, 429, auth expiry, schema change | Classify transient vs permanent; retry transient; alert on permanent |
| AI | Malformed output, schema violation, hallucination, refusal, timeout | Validate output; retry once with repair prompt; fall back; escalate |
| Business | Invalid state (order already shipped, duplicate customer) | Explicit branch; don't treat as exception |
| Infrastructure | Network, database, queue, service down | Retry with backoff; circuit-break; degrade or park |
| Human | Rejection, timeout, reviewer unavailable | Defined timeout path, escalation, default-safe outcome |

Decide per error: retry, compensate, park for review, or fail loudly. "Log and continue" needs a stated reason.

## 2. Retry architecture

For each retryable operation define: retry condition, max attempts, initial delay, backoff (exponential is the usual default), jitter (to avoid synchronized retry storms), retry scope (this call, this step, whole workflow), and idempotency.

- Retry only transient failures (timeouts, 429, 5xx). Retrying a 400 or an auth failure just repeats the failure.
- Respect rate-limit hints (`Retry-After`) when the API provides them.
- Never retry a non-idempotent operation blindly: a timeout does not mean the call failed, only that you didn't hear back.
- After retries are exhausted, send the item somewhere inspectable (dead-letter queue, failure table, review task) with enough context to replay it.

## 3. Idempotency

Identify operations where running twice causes damage: payments, order creation, record creation, sending email/messages, external API mutations. Triggers are usually at-least-once, so duplicates are normal, not exceptional.

For each, define: **idempotency key** (what uniquely identifies the intended operation — e.g. source event ID, or a hash of business keys; not a fresh random value per attempt), **generation** (where/when created, before the first attempt), **storage** (where seen-keys live), **validation** (check-then-act must be atomic or the receiving API must enforce it), **expiration** (how long keys are remembered, longer than the maximum retry/replay window), and **recovery** (what happens if the key store is unavailable).

If the downstream API supports idempotency keys, use them; if not, the workflow must dedupe itself, or the step must be designed as a safe upsert.

## 4. Timeouts

Every external dependency gets one. Define connection timeout, execution timeout, AI-call timeout (LLM calls are slow and variable), human-approval timeout, and an overall workflow timeout. A missing timeout is how a single slow dependency stalls everything. Timeouts must be shorter than any caller's own timeout, or the caller retries while the original is still running.

## 5. Partial failure and recovery

Ask: if step 4 of 6 fails after step 3 sent an email, what is the state? Options: **resume** from persisted state; **compensate** (saga: undo or counteract earlier side effects); **park** for manual completion; **restart** only if all prior steps are idempotent. Put side effects that cannot be undone (sending, paying, deleting) as late as possible and behind validation or approval.

## 6. Human-in-the-loop

Flow: automated processing → risk/confidence check → human review → approve / reject / modify → continue.

Require human review when confidence is low, financial or legal impact is high, the action is irreversible, communication is sensitive or external, or policy demands it. Define:
- What the reviewer sees (inputs, AI output, reasoning/evidence, the exact action that will be taken)
- Allowed outcomes, including edit
- Timeout and escalation (who next, after how long) and the **default-safe outcome** if nobody answers (usually: do not proceed)
- How the decision is recorded (who, when, what) for audit
- What happens to the workflow while waiting (persisted state, not an open connection)

## 6b. Waiting on an external party (not a reviewer)

Some steps wait for someone outside the team: a candidate confirming an interview time, a customer replying, a supplier sending a document, a webhook callback from another system. Nobody is obliged to answer, so a design with no limit waits forever and quietly leaks work. For each such step define:

- **Wait limit**: how long to wait before acting (a business decision; if unknown write NOT PROVIDED and raise it as an open question).
- **Reminder**: whether, when and how often to nudge the other party, and who approves the message.
- **Expiry path**: what happens when the limit passes (release held resources such as calendar slots, notify the owner, close or park the item, never proceed as if they had agreed).
- **Late reply**: what happens if the answer arrives after expiry (reopen, or ignore with a message).
- **Matching**: how the reply is tied back to the right item (idempotency key, correlation ID, signed link), so a wrong or duplicate reply cannot confirm something else.

Model the wait as persisted state with a due time, not an open connection. Give the step a type that says it waits (`wait for reply`, `callback`), because the validator then requires a real Timeout cell.

## 7. State and resumption

Long or human-gated workflows need persisted state: current step, inputs, outputs of completed steps, idempotency keys, correlation ID. Without it, a restart repeats side effects or loses work. Say where state lives and who owns it; avoid hidden state.

## 8. Per-step reliability checklist

- [ ] Failure behavior stated (retry / compensate / park / fail)
- [ ] Retry policy or explicit "no retry" with reason
- [ ] Timeout set (for steps that wait on a person or outside reply: wait limit, reminder, expiry path)
- [ ] Idempotent, or protected by an idempotency key
- [ ] Side effect classified (read-only / reversible / irreversible)
- [ ] Irreversible effects behind validation or approval
- [ ] Failure is observable (logged, metric, alert if it matters)
- [ ] Recovery path exists for exhausted retries
