# Chaining the three skills

`ai-requirements-analyst` → `ai-system-architect` → `ai-workflow-architect`

This file is identical in all three skills. It explains how to run them one after another so each stage builds on the last without losing, restating or contradicting anything.

## Contents
1. The chain at a glance
2. Running it, one stage at a time
3. The four conventions
4. When the user is not there to answer questions
5. What the validators check, and the order to run them
6. Common chain errors and the fix
7. Using a skill on its own

## 1. The chain at a glance

| Stage | Skill | Reads | Writes (suggested name) | Owns these IDs |
|---|---|---|---|---|
| 1 | `ai-requirements-analyst` | the user's idea, notes or documents | `01-requirements.md` | BO ST ACT FR NFR BR DR IR AIR AR UC US AC CON DEP |
| 2 | `ai-system-architect` | `01-requirements.md` | `02-architecture.md` | AD ADR RISK DEBT INT EVT COMP |
| 3 | `ai-workflow-architect` | `01-requirements.md` and `02-architecture.md` | `03-workflow.md` | WR WD STEP DEC TOOL TASK TEST WADR WRISK |
| all | shared | | | **A** (assumption) and **Q** (open question): every stage adds new numbers |

Why the split matters: requirements say *what and why*, architecture says *what the system is made of*, the workflow says *what happens, step by step, when it fails, and who approves*. A stage must not redo the previous stage's job; it cites the earlier IDs and adds only its own.

## 2. Running it, one stage at a time

The user can say "run the chain" or run each skill by hand. Either way, the same four moves per stage:

1. **Read everything upstream first.** Open every earlier document completely before writing. Extract what it already answers; never ask the user something an earlier document settled.
2. **Write only your own IDs.** Cite upstream IDs (`FR-003`, `ADR-002`) wherever you rely on them; do not copy their definitions again.
3. **Finish with the Handoff block** (section 3) and put the Chain header on the first lines.
4. **Validate, fix, then pass the file on.**

```bash
# after stage 1
python3 scripts/validate_ids.py 01-requirements.md
# after stage 2
python3 scripts/validate_ids.py 02-architecture.md
python3 scripts/validate_chain.py 01-requirements.md 02-architecture.md
# after stage 3
python3 scripts/validate_workflow.py 03-workflow.md
python3 scripts/validate_diagrams.py 03-workflow.md
python3 scripts/validate_chain.py 01-requirements.md 02-architecture.md 03-workflow.md
```

The validators read the `upstream=` files named in the Chain header (when they sit in the same folder), so no flags are needed. Use `--upstream a.md b.md` only when the earlier documents live elsewhere. If the header names files that cannot be found, citations of upstream IDs are reported as "not verified" instead of as errors.

Prompts that work (adapt the file names):

- Stage 1: "Use ai-requirements-analyst on this brief. Save it as 01-requirements.md."
- Stage 2: "Use ai-system-architect on 01-requirements.md. Save it as 02-architecture.md."
- Stage 3: "Use ai-workflow-architect on 01-requirements.md and 02-architecture.md. Save it as 03-workflow.md."

## 3. The four conventions

### 3.1 Chain header (first lines of every document)

```text
> Chain: stage=2 | skill=ai-system-architect | upstream=01-requirements.md | next=ai-workflow-architect
```

Stage 1 writes `upstream=none`; stage 3 writes `next=none`. Stage 3 also writes `Depth: quick|standard|full` on its own line near the top so validators and the report generator check it at the depth it was written for.

### 3.2 IDs: one owner, cite everywhere

- A document **defines** an ID once, in the first cell of a table row, a list item, a heading, or at the start of a bold or plain line. Anywhere else the ID is a **citation**.
- The stage that owns a prefix defines it. A later stage never redefines it: no copying `BO-001` or `CON-001` rows into the next document. Cite them. If a restatement helps readers, put it under a subheading named **Carried forward from upstream**; everything under it counts as citation only.
- A table that lists an upstream ID next to the downstream thing that handles it (a requirement table with a "Source" column, a "Business objective" table with an "Upstream ID" column) must put the downstream ID, or a descriptive cell, **first**, and the upstream ID in a later cell. The first cell is what defines.
- Ranges are fine: "FR-001 to FR-013" cites all thirteen.
- **A and Q are one numbered sequence across the whole chain.** Stage 1 ends at A-008 and Q-006, so stage 2's first new ones are A-009 and Q-007, and so on. The Handoff block says what the next number is.
- Never renumber an ID once any document cites it. Retire it and say so.

### 3.3 Handoff block (last section of stages 1 and 2; optional for stage 3)

```text
## Handoff to next stage
- Next skill: ai-system-architect
- Must cover: FR-001 to FR-013, NFR-001, NFR-003, BR-001, BR-002, AIR-001, AIR-002
- Locked decisions: BR-001
- Blocking questions: Q-001, Q-004, Q-005
- Next A: 009
- Next Q: 007
```

- **Must cover**: Must-priority items the next stages cannot drop. Every later document must cite each one, as covered, deferred (with a reason), or out of scope (with a reason).
- **Locked decisions**: decisions that must not be silently changed or overridden downstream (for example "a recruiter, not software, rejects a candidate"). A later stage may challenge one, but only in the open, by citing it and recording the reason as a new open question or ADR.
- **Blocking questions**: unanswered questions whose answer could change the next stage's design.
- **Next A / Next Q**: the first free numbers, written as plain numbers (`009`, not `A-009`, because that ID does not exist yet and would read as a dangling citation).

If a stage changes an upstream **priority** (say a "Should" becomes "Optional"), it states the old and new priority and the reason, next to the item, and cites the upstream ID.

### 3.4 Coverage: cite everything upstream, or say why not

Every stage 2 and stage 3 document includes a coverage table under a heading containing "Coverage" or "Traceability" that lists each upstream item and where this document handles it, or the words *deferred*, *out of scope* or *not applicable* with a reason:

| Upstream | Handled by |
|---|---|
| FR-001 to FR-004 | stage 2: COMP-001, COMP-002 · stage 3: WR-001 to WR-004 |
| FR-007 (review queue) | a user-interface task (TASK-008), not a workflow step |
| NFR-004 | no target defined upstream, so nothing to test (stated in cost section) |

Citing is the minimum bar the validators can check. It shows an item was considered, not that it was handled well; the reviewer still reads the content.

## 4. When the user is not there to answer questions

The skills normally ask 3–6 grouped questions. In a chain that is run in one go ("run the chain", "proceed with assumptions", or the user is simply unavailable), do not stall:

1. Proceed on labeled assumptions (`A-###`, with the impact if wrong).
2. Record each question as `Q-###`, with *why it matters* and what design choice depends on it.
3. Put the questions that could change the next stage under **Blocking questions** in the Handoff.
4. At the end of the chain, present all open questions together, once, grouped by who can answer them, with the stage each one affects.

When the user can answer between stages, ask the blocking questions first, update the earlier document (keep IDs stable, record the answer next to the question), then continue. If an answer changes an upstream document, re-run the later stages that cited the changed items; `validate_chain.py` shows which citations are affected.

## 5. What the validators check, and the order to run them

| Command | Checks |
|---|---|
| `validate_ids.py <doc> [--upstream ...]` | Duplicate, dangling and malformed IDs by one shared definition grammar; with `--upstream`, citations resolve against earlier documents and restating an upstream ID is an error. Stage 1 also checks that every `FR-nnn` has an `AC-nnn-n`. |
| `validate_workflow.py <doc> [--depth] [--upstream ...]` | Required sections for the depth, step table columns, failure / retry / timeout per step, human and external-wait steps have a timeout path, traceability, unlabeled money / percentage / volume figures anywhere, leaked secrets, agent specification, placeholders. |
| `validate_diagrams.py <doc>` | Mermaid syntax, diagram IDs exist, decision nodes have branches. |
| `validate_chain.py <01> <02> <03>` | The hand-off: stage order, one definition per ID, no forward or dangling citations, A/Q numbering continues, upstream questions and assumptions are carried, coverage of upstream items, Handoff items cited downstream, shared scripts not drifted. |

Validators check structure. They cannot tell whether a design is good, whether a claim about an API is true, or whether an assumption is reasonable. The documents must still be read.

## 6. Common chain errors and the fix

| Message | Cause | Fix |
|---|---|---|
| `defined in more than one document` | A later document restated an upstream row or reused an A/Q number | Replace with a citation, or move under "Carried forward from upstream"; give new A/Q the next free number |
| `cites ID(s) defined in no document` | Typo, or an invented requirement | Fix the ID, or add the requirement upstream first |
| `cites ID(s) that exist only in a LATER document` | Documents passed in the wrong order, or an earlier stage refers forward | Pass 1, 2, 3 in order; remove the forward reference |
| `upstream items never cited` | An upstream requirement, ADR, integration or component was dropped silently | Cover it, or list it in the coverage table as deferred or out of scope with a reason |
| `does not cite must cover / locked decisions / blocking questions` | The Handoff promised something the later document ignores | Cite and handle it, or challenge it openly |
| `no acceptance criterion` (stage 1) | A functional requirement cannot be verified | Add `AC-<FR number>-1` in Given / When / Then form, or say why it cannot be tested |
| `Timeout is 'N/A' but the step waits` | A step waits on a person or an outside reply with no limit | State the wait limit (or NOT PROVIDED) and the reminder or expiry path |
| `figure ... without an evidence tag` | A number with no origin | Tag it `[STATED]`, `[ASSUMED]`, `[RECOMMENDED]`, or write NOT PROVIDED |

## 7. Using a skill on its own

Nothing here is required for a stand-alone run. Without upstream documents, write `upstream=none` in the header, define whatever IDs you need (including `BO-###` in the workflow skill), and skip `--upstream` and `validate_chain.py`. The first time a stand-alone document is later fed into the chain, add the header and Handoff block and pass it to the next stage as stage 1 or 2.
