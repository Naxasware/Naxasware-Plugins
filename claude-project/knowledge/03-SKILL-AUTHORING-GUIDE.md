# Writing skills that work

## Turning an instruction document into a skill
| In the document | Goes to |
|---|---|
| Purpose, who it's for, when to use it | `description` (what + when) and a short intro in SKILL.md |
| Core workflow / decision logic | SKILL.md body (keep it scannable) |
| Hard rules and constraints | SKILL.md "Rules that always apply", each with its reason |
| Long templates, schemas, taxonomies, worked examples, glossaries | `references/*.md`, linked from SKILL.md with a line on *when* to read each |
| Repetitive, exact, mechanical steps (validation, formatting, conversion) | `scripts/*.py` |
| Sample inputs/outputs | `examples/` |
Preserve the author's intent and content. Don't add capabilities the document doesn't describe. If something is ambiguous or missing, list it under assumptions or open questions for the owner.

## The description is the trigger
It is the only text Claude sees when deciding to use the skill. Make it do work:
- Say what the skill does and when to use it.
- Include realistic phrasings, including ones that don't name the skill ("turn this into a spec", "does our code match our docs").
- Lean slightly assertive ("Use whenever…, even if the user doesn't say…"); Claude tends to under-trigger skills.
- State non-goals in one clause if confusion is likely.
- ≤ 1024 characters, single paragraph, no XML/angle brackets.

## Structure: progressive disclosure
1. Metadata (always in context): name + description.
2. SKILL.md body (loaded on trigger): under 500 lines.
3. `references/`, `scripts/` (loaded/run only when needed). For a reference file over ~300 lines, add a short table of contents at its top.

## Style
- Imperative, plain language. Explain *why* behind rules; avoid shouting ALWAYS/NEVER when a reason would do.
- Prefer examples and output templates over abstract description.
- Keep one canonical place per fact; link instead of repeating.
- Generalize from examples so it works beyond the ones you saw; don't overfit to a single sample.
- Be honest about limits: if the skill can't verify something, it should say so rather than assert it.

## Safety
No malware, exploit code, deceptive behavior, or content that would surprise the user given the skill's stated purpose. Read-only by default for anything touching external systems; writes need explicit authorization.

## Scripts
Only when they beat prose: exact validation, format conversion, deterministic transforms. Standard library, clear `--help`, meaningful exit codes, no network calls unless essential (and then documented).

## Quick self-review before delivering
- [ ] Would a user's plausible phrasing trigger this? Would an unrelated request not?
- [ ] Is SKILL.md under 500 lines and every referenced file present?
- [ ] Does every rule say why?
- [ ] Are unknowns flagged rather than invented?
- [ ] Are names, version, CHANGELOG entry, and README consistent?
