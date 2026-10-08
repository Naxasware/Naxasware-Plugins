#!/usr/bin/env python3
"""
Validate the hand-off between the documents of the chain:

    1 ai-requirements-analyst  ->  2 ai-system-architect  ->  3 ai-workflow-architect

Run it after each stage (with the documents produced so far) and once at the end:

    python3 validate_chain.py 01-requirements.md 02-architecture.md 03-workflow.md [--strict]

Documents are given in stage order (or carry `stage=` in their Chain header).
This file is the same in all three skills; it needs `idscan.py` next to it.

What it checks (E = error, W = warning)
  header      each document starts with a `Chain:` line (stage, skill, upstream,
              next); stage numbers ascend and match the skill            [W / E]
  identity    an ID is defined in exactly one document (restating an upstream
              ID in a later document is a collision)                      [E]
  resolution  every cited ID is defined in the same or an EARLIER document;
              citing an ID that exists only in a LATER document, or nowhere,
              is an error. Ranges ("FR-001 to FR-013") are expanded       [E]
  numbering   A- and Q- are shared sequences: a later document continues after
              the highest upstream number                                 [W]
  carry-over  every upstream A- and Q- is cited again in each later
              document (carried, answered, or marked superseded)          [W]
  coverage    (IDs written out in full, or a range inside a table row, count; a
              prose range such as "FR-001 to FR-013" does not)
              every upstream FR, NFR, BR, AIR, IR, CON, DEP is cited in each
              later document; every ADR, INT, COMP from stage 2 and every AC
              from stage 1 is cited in stage 3. Citing is the minimum bar:
              it proves the item was looked at, not that it was done well [W]
  handoff     each non-final document has a `Handoff` section; IDs listed under
              `Must cover`, `Locked decisions` and `Blocking questions` are
              cited in every later document                               [E]
  drift       idscan.py / validate_chain.py differ from the sibling skills'
              copies                                                      [W]

Exit code 1 on any error (or any warning with --strict). Standard library only.
"""

import hashlib
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import idscan  # noqa: E402

COVER_FROM_1 = ["FR", "NFR", "BR", "AIR", "IR", "CON", "DEP"]   # must be cited by stages 2 and 3
COVER_FROM_2 = ["ADR", "INT", "COMP"]                            # must be cited by stage 3
COVER_AC = ["AC"]                                                # must be cited by stage 3
HEADER_RE = re.compile(r"^\s*>?\s*\**Chain\**\s*:\s*(.+?)\s*$", re.I)
HANDOFF_KEYS = {
    "must cover": "must", "locked decisions": "locked", "blocking questions": "blocking",
    "next a": "next_a", "next q": "next_q", "next skill": "next_skill",
}


# ---------------------------------------------------------------- parsing

def parse_header(text):
    for line in text.splitlines()[:25]:
        m = HEADER_RE.match(line)
        if m:
            fields = {}
            for part in re.split(r"[|;]", m.group(1)):
                if "=" in part:
                    k, v = part.split("=", 1)
                    fields[k.strip().lower()] = v.strip().strip("`")
            return fields
    return None


def ids_in(text):
    out = set()
    for m in idscan.ID_RE.finditer(text):
        if len(m.group(2)) >= 3:
            out.add(idscan.norm(m.group(1), m.group(2), m.group(3)))
    out.update(idscan._expand_ranges(text))
    return out


def parse_handoff(text):
    """Return {key: text} for the Handoff section, or None if there is none."""
    lines = text.splitlines()
    start = level = None
    in_fence = False
    for n, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_fence = not in_fence
        m = idscan.HEADING_RE.match(line.strip()) if not in_fence else None
        if m and start is None and re.search(r"hand-?off", m.group(2), re.I):
            start, level = n, len(m.group(1))
        elif m and start is not None and len(m.group(1)) <= level:
            lines = lines[start + 1:n]
            break
    else:
        lines = lines[start + 1:] if start is not None else None
    if lines is None:
        return None
    out = {}
    for line in lines:
        m = re.match(r"^\s*(?:[-*+]\s+)?\**([A-Za-z ]+?)\**\s*:\s*(.*)$", line)
        if m and m.group(1).strip().lower() in HANDOFF_KEYS:
            out[HANDOFF_KEYS[m.group(1).strip().lower()]] = m.group(2)
    return out


def short(ids, n=8):
    ids = sorted(ids)
    return ", ".join(ids[:n]) + (f" … (+{len(ids) - n} more)" if len(ids) > n else "")


# ---------------------------------------------------------------- main check

def validate(paths, texts=None):
    errors, warnings = [], []
    texts = texts or [Path(p).read_text(encoding="utf-8") for p in paths]
    names = [Path(p).name for p in paths]
    n = len(paths)
    heads = [parse_header(t) for t in texts]

    # --- header and stage order
    stages = []
    for k in range(n):
        h = heads[k]
        pos = k + 1 if n == 3 else None
        if h is None:
            warnings.append(f"{names[k]}: no `Chain:` header in the first lines "
                            f"(expected: Chain: stage=N | skill=... | upstream=... | next=...)")
            stages.append(pos if pos else k + 1)
            continue
        try:
            st = int(h.get("stage", "").split()[0])
        except (ValueError, IndexError):
            warnings.append(f"{names[k]}: Chain header has no numeric stage=")
            st = pos if pos else k + 1
        stages.append(st)
        skill = h.get("skill")
        if skill and idscan.SKILL_STAGE.get(skill) not in (None, st):
            errors.append(f"{names[k]}: Chain header says stage={st} but skill={skill} is stage {idscan.SKILL_STAGE[skill]}")
    if stages != sorted(stages) or len(set(stages)) != len(stages):
        errors.append(f"documents are not in ascending stage order (stages {stages}); pass them as 1, 2, 3")

    scans = [idscan.scan(t) for t in texts]
    defined_in = defaultdict(list)           # id -> [doc index]
    for k, s in enumerate(scans):
        for i in s.defs:
            defined_in[i].append(k)

    # --- identity
    groups = defaultdict(list)
    for i, ks in sorted(defined_in.items()):
        if len(ks) > 1:
            groups[tuple(ks)].append(i)
        for k in ks:
            ps = idscan.stage_of_prefix(idscan.prefix_of(i))
            if ps not in (None, 0) and ps != stages[k]:
                warnings.append(f"{names[k]}: {i} is a stage-{ps} ID defined in a stage-{stages[k]} document")
    for ks, ids in groups.items():
        errors.append(f"{len(ids)} ID(s) are defined in more than one document ({' and '.join(names[k] for k in ks)}): "
                      f"{short(ids, 10)}. Define each ID once and cite it elsewhere "
                      f"(restated rows belong under a 'Carried forward' heading)")

    # --- resolution
    for k, s in enumerate(scans):
        bad_fwd, bad_none = [], []
        for i in sorted(set(s.refs) | set(s.fence_ids)):
            ks = defined_in.get(i)
            if ks and min(ks) <= k:
                continue
            (bad_fwd if ks else bad_none).append(i)
        if bad_none:
            errors.append(f"{names[k]}: cites ID(s) defined in no document: {short(bad_none)}")
        if bad_fwd:
            errors.append(f"{names[k]}: cites ID(s) that exist only in a LATER document: {short(bad_fwd)}")
        for no, tok in s.malformed:
            warnings.append(f"{names[k]}: line {no}: malformed ID '{tok}'")

    cited = [set(s.refs) | set(s.fence_ids) | set(s.defs) for s in scans]
    # coverage needs a real citation: written out in full, or a range inside a table row
    cov = [s.explicit | s.table_ranges | set(s.defs) for s in scans]

    # --- shared numbering (A, Q)
    for p in idscan.SHARED:
        prev_max = 0
        for k, s in enumerate(scans):
            nums = sorted(idscan.number_of(i) for i in s.defs if idscan.prefix_of(i) == p and i.count("-") == 1)
            if not nums:
                continue
            if prev_max and nums[0] != prev_max + 1:
                warnings.append(f"{names[k]}: first new {p}- is {p}-{nums[0]:03d} but upstream ends at "
                                f"{p}-{prev_max:03d}; continue numbering at {p}-{prev_max + 1:03d}")
            if nums != list(range(nums[0], nums[0] + len(nums))):
                warnings.append(f"{names[k]}: {p}- numbering has gaps ({nums})")
            prev_max = max(prev_max, nums[-1])

    # --- carry-over and coverage
    def upstream_ids(k, prefixes):
        return sorted(i for j in range(k) for i in scans[j].defs
                      if idscan.prefix_of(i) in prefixes
                      and i.count("-") == (2 if idscan.prefix_of(i) == "AC" else 1))

    for k in range(1, n):
        missing = [i for i in upstream_ids(k, idscan.SHARED) if i not in cited[k]]
        if missing:
            warnings.append(f"{names[k]}: upstream assumptions/questions not carried, answered or superseded: {short(missing)}")
        st = stages[k]
        want = list(COVER_FROM_1)
        if st >= 3:
            want += COVER_FROM_2 + COVER_AC
        miss_cov = [i for i in upstream_ids(k, set(want))
                    if i not in cov[k] and idscan.stage_of_prefix(idscan.prefix_of(i)) < st]
        if miss_cov:
            warnings.append(f"{names[k]}: upstream items never cited (covered, deferred or marked out of scope): {short(miss_cov, 14)}")

    # --- handoff
    for k in range(n):
        ho = parse_handoff(texts[k])
        if ho is None:
            if k < n - 1 or (heads[k] and heads[k].get("next") not in (None, "", "none")):
                warnings.append(f"{names[k]}: no `Handoff` section (Must cover / Locked decisions / Blocking questions)")
            continue
        for key, label in (("must", "Must cover"), ("locked", "Locked decisions"), ("blocking", "Blocking questions")):
            ids = ids_in(ho.get(key, ""))
            undefined = [i for i in ids if i not in defined_in or min(defined_in[i]) > k]
            if undefined:
                errors.append(f"{names[k]}: Handoff `{label}` lists undefined ID(s): {short(undefined)}")
            for j in range(k + 1, n):
                pool = cov[j] if key == "must" else cited[j]
                gone = [i for i in sorted(ids) if i not in pool and i not in undefined]
                if gone:
                    errors.append(f"{names[j]}: does not cite {label.lower()} ID(s) from {names[k]}: {short(gone)}")
        for key, p in (("next_a", "A"), ("next_q", "Q")):
            m = re.search(r"\d+", ho.get(key, ""))
            if m and k + 1 < n:
                want = int(m.group())
                new = sorted(idscan.number_of(i) for i in scans[k + 1].defs
                             if idscan.prefix_of(i) == p and i.count("-") == 1)
                if new and new[0] != want:
                    warnings.append(f"{names[k + 1]}: Handoff of {names[k]} says the next {p}- number is {want:03d}, "
                                    f"but the first new one is {p}-{new[0]:03d}")
                used = [i for i in scans[k].defs if idscan.prefix_of(i) == p and i.count("-") == 1]
                if used and want <= max(idscan.number_of(i) for i in used):
                    warnings.append(f"{names[k]}: Handoff says the next {p}- number is {want:03d} but "
                                    f"{p}-{max(idscan.number_of(i) for i in used):03d} is already used")

    # --- drift between the copies shipped with each skill
    here = Path(__file__).resolve().parent
    for fname in ("idscan.py", "validate_chain.py"):
        mine = hashlib.sha256((here / fname).read_bytes()).hexdigest()
        for sib in here.parent.parent.glob(f"ai-*/scripts/{fname}"):
            if sib.resolve() != (here / fname).resolve() and hashlib.sha256(sib.read_bytes()).hexdigest() != mine:
                warnings.append(f"{fname} differs from {sib.parent.parent.name}/scripts/{fname}; "
                                f"the three copies must be identical")
    return errors, warnings


def main(argv):
    strict = "--strict" in argv
    paths = [a for a in argv if not a.startswith("--")]
    if len(paths) < 2:
        print(__doc__)
        return 2
    missing = [p for p in paths if not Path(p).exists()]
    if missing:
        print(f"ERROR: file(s) not found: {', '.join(missing)}")
        return 1
    errors, warnings = validate(paths)
    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    print(f"chain of {len(paths)} document(s): {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors or (strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
