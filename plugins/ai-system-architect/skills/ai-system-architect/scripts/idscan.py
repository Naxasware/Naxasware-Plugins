#!/usr/bin/env python3
"""
Shared ID scanner for the ai-requirements-analyst -> ai-system-architect ->
ai-workflow-architect chain.

This file is copied byte-for-byte into each skill's scripts/ folder so every
skill stays self-contained when packaged. Do not edit one copy on its own:
change it once, then re-copy to the other two (the chain validator warns when
the copies drift apart).

What it defines
---------------
* The ID prefixes each stage OWNS (it is the only stage that may define them)
  and the prefixes that are SHARED (A, Q: every stage adds new numbers).
* ONE grammar for "this line defines an ID", the same in every validator:
  an ID that is the first thing in a heading, list item, table row (first
  cell), bold line or plain line, outside code fences, and not under a
  heading that only references (Traceability, Coverage, Cross-reference,
  Carried forward, Upstream). `<!-- ref -->` on a line forces reference-only.
* Range references: "FR-001 to FR-013", "A-001–A-008", "Q-001..Q-004" count as
  references to every ID in the range (so they resolve). For COVERAGE checks only
  IDs written out in full, or implied by a range inside a table row, count: a
  prose sentence "FR-001 to FR-013" does not prove each requirement was handled.

Standard library only.
"""

import re
from collections import defaultdict

# ---------------------------------------------------------------- prefixes

OWNED = {
    1: ["BO", "ST", "ACT", "FR", "NFR", "BR", "DR", "IR", "AIR", "AR", "UC",
        "US", "AC", "CON", "DEP"],                                   # requirements
    2: ["AD", "ADR", "RISK", "DEBT", "INT", "EVT", "COMP"],          # architecture
    3: ["WR", "WD", "STEP", "DEC", "TOOL", "TASK", "TEST", "WADR", "WRISK"],  # workflow
}
SHARED = ["A", "Q"]  # every stage defines new numbers; numbering continues across stages

STAGE_SKILL = {
    1: "ai-requirements-analyst",
    2: "ai-system-architect",
    3: "ai-workflow-architect",
}
SKILL_STAGE = {v: k for k, v in STAGE_SKILL.items()}


def stage_of_prefix(prefix):
    """Stage that owns a prefix, 0 for shared, None for unknown."""
    if prefix in SHARED:
        return 0
    for st, prefixes in OWNED.items():
        if prefix in prefixes:
            return st
    return None


ALL_PREFIXES = sorted({p for ps in OWNED.values() for p in ps} | set(SHARED), key=len, reverse=True)
_ALT = "|".join(ALL_PREFIXES)

# PREFIX-NNN or PREFIX-NNN-N (sub ids such as AC-007-1). Not preceded or
# followed by letters/digits/underscore, so NFR-001 never matches as FR-001.
ID_RE = re.compile(r"(?<![A-Za-z0-9_-])(" + _ALT + r")-(\d+)(?:-(\d+))?(?![A-Za-z0-9_])")
LEAD_RE = re.compile(
    r"^(?:#{1,6}\s+|[-*+]\s+|\d+[.)]\s+|\|\s*|>\s*)*(?:\*\*|__|`)?\s*(" + _ALT
    + r")-(\d+)(?:-(\d+))?(?![A-Za-z0-9_])"
)
RANGE_RE = re.compile(
    r"(?<![A-Za-z0-9_-])(" + _ALT + r")-(\d{3,4})\s*(?:to|through|–|—|\.\.\.?)\s*(?:(?:" + _ALT
    + r")-)?(\d{3,4})(?![A-Za-z0-9_])", re.I)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
REF_ONLY_HEADING_RE = re.compile(r"traceab|coverage|cross-?ref|carried forward|upstream", re.I)


class Scan:
    """Result of scanning one document."""

    def __init__(self):
        self.defs = defaultdict(list)       # id -> [line numbers]
        self.def_text = {}                  # id -> text of first defining line
        self.refs = defaultdict(list)       # id -> [line numbers] (non-defining uses)
        self.malformed = []                 # (line, token)
        self.line_ids = {}                  # line no -> [ids] (non-fence lines)
        self.fence_ids = defaultdict(list)  # id -> [line numbers] inside code fences
        self.explicit = set()               # ids written out in full (not only implied by a range)
        self.table_ranges = set()           # ids implied by a range inside a table row (a mapping)
        self.prefixes = set(ALL_PREFIXES)


def norm(prefix, digits, sub=None):
    return f"{prefix}-{digits}" + (f"-{sub}" if sub else "")


def _expand_ranges(line):
    """Yield every ID implied by 'X-001 to X-004' style ranges on a line."""
    for m in RANGE_RE.finditer(line):
        p, lo, hi = m.group(1), int(m.group(2)), int(m.group(3))
        if lo < hi and hi - lo <= 200:
            width = len(m.group(2))
            for n in range(lo, hi + 1):
                yield f"{p}-{n:0{width}d}"


def scan(text, prefixes=None):
    """Scan a document. `prefixes` limits which prefixes count (default: all)."""
    allowed = set(prefixes) if prefixes else set(ALL_PREFIXES)
    s = Scan()
    s.prefixes = allowed
    in_fence = False
    heading = ""
    for no, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        hm = HEADING_RE.match(stripped) if not in_fence else None
        if hm:
            heading = hm.group(2)

        found = []
        for m in ID_RE.finditer(line):
            p, d, sub = m.group(1), m.group(2), m.group(3)
            if p not in allowed:
                continue
            if len(d) < 3:
                s.malformed.append((no, norm(p, d, sub)))
                continue
            found.append(norm(p, d, sub))
        extra = [i for i in _expand_ranges(line) if i.split("-")[0] in allowed]
        if not found and not extra:
            continue

        if in_fence:
            for i in found + extra:
                s.fence_ids[i].append(no)
            continue

        s.line_ids[no] = list(found)
        s.explicit.update(found)
        if stripped.startswith("|"):
            s.table_ranges.update(extra)
        defined = None
        if not REF_ONLY_HEADING_RE.search(heading) and "<!-- ref" not in line:
            lm = LEAD_RE.match(stripped)
            if lm and len(lm.group(2)) >= 3 and lm.group(1) in allowed:
                defined = norm(lm.group(1), lm.group(2), lm.group(3))
        used = list(found)
        if defined:
            s.defs[defined].append(no)
            s.def_text.setdefault(defined, stripped)
            if defined in used:
                used.remove(defined)  # drop one occurrence: the definition itself
        for i in used + extra:
            s.refs[i].append(no)
    return s


def prefix_of(i):
    return i.split("-")[0]


def number_of(i):
    return int(i.split("-")[1])


# ---------------------------------------------------------------- chain header

CHAIN_RE = re.compile(r"^\s*>?\s*\**Chain\**\s*:\s*(.+?)\s*$", re.I)


def chain_upstream_names(text):
    """File names listed in the `upstream=` field of the Chain header; [] if none or no header."""
    for line in text.splitlines()[:25]:
        m = CHAIN_RE.match(line)
        if m:
            for part in re.split(r"[|;]", m.group(1)):
                if part.strip().lower().startswith("upstream"):
                    val = part.split("=", 1)[1].strip().strip("`") if "=" in part else ""
                    if val.lower() in ("", "none"):
                        return []
                    return [v.strip().strip("`") for v in val.split(",") if v.strip()]
            return []
    return []


def auto_upstream(doc_path, text, explicit_paths=None):
    """
    Decide the upstream context for a document.
    Returns (upstream {id: file} or None, chained: bool, note or None).
    explicit_paths (from --upstream) win; otherwise the Chain header's upstream files are
    used when they sit next to the document. If the header names upstream files that cannot
    be found, `chained` is True so that citations of upstream A-/Q- IDs are not misreported
    as undefined.
    """
    from pathlib import Path
    if explicit_paths:
        return load_upstream(explicit_paths), True, None
    names = chain_upstream_names(text)
    if not names:
        return None, False, None
    folder = Path(doc_path).resolve().parent
    found = [folder / n for n in names if (folder / n).exists()]
    if len(found) == len(names):
        return load_upstream(found), True, "upstream resolved from the Chain header: " + ", ".join(names)
    return None, True, "Chain header lists upstream files that were not found next to the document; citations of upstream IDs are not verified"


# ---------------------------------------------------------------- checking

def load_upstream(paths):
    """Scan upstream documents. Returns {id: filename} of everything they define."""
    from pathlib import Path
    out = {}
    for p in paths:
        s = scan(Path(p).read_text(encoding="utf-8"))
        for i in s.defs:
            out.setdefault(i, Path(p).name)
    return out


def check_doc(s, stage, upstream=None, malformed_is_error=False, gaps=True, orphans=False,
              orphan_prefixes=(), chained=False):
    """
    Check one scanned document that belongs to `stage` (1, 2 or 3).

    upstream: {id: filename} from earlier stages (see load_upstream), or None
              when the document is checked on its own.
    Returns (errors, warnings).
    """
    errors, warnings = [], []
    local = {prefix_of(i) for i in s.defs} if upstream is None else set()
    # Checked on its own, a document may define any prefix itself (e.g. a workflow
    # document that defines its own BO-###); with upstream, only its stage's prefixes.
    own = lambda p: stage_of_prefix(p) in (stage, 0) or p in local

    for i, lines in sorted(s.defs.items()):
        if len(lines) > 1:
            errors.append(f"{i} is defined {len(lines)} times (lines {', '.join(map(str, lines))})")

    for no, tok in s.malformed:
        msg = f"line {no}: malformed ID '{tok}' (use at least three digits, e.g. {tok.split('-')[0]}-001)"
        (errors if malformed_is_error else warnings).append(msg)

    # IDs defined here whose prefix belongs to another stage
    for i, lines in sorted(s.defs.items()):
        ps = stage_of_prefix(prefix_of(i))
        if upstream is not None and i in upstream and ps != 0:
            errors.append(f"{i} (line {lines[0]}) is already defined in {upstream[i]}; reference it "
                          f"instead of redefining it (or put the restatement under a 'Carried forward' heading)")
        elif upstream is not None and i in upstream and ps == 0:
            errors.append(f"{i} (line {lines[0]}) is already defined in {upstream[i]}; "
                          f"A/Q numbering continues across stages, pick the next free number")
        elif upstream is not None and ps is not None and ps not in (stage, 0):
            if ps < stage:
                warnings.append(f"{i} (line {lines[0]}) uses a stage-{ps} prefix but is not defined upstream; "
                                f"add it upstream or use a stage-{stage} prefix")
            else:
                warnings.append(f"{i} (line {lines[0]}) uses a stage-{ps} prefix (a later stage's ID) in a stage-{stage} document")

    # References
    unresolved_upstream = defaultdict(list)
    for i, lines in sorted(s.refs.items()):
        if i in s.defs:
            continue
        p = prefix_of(i)
        ps = stage_of_prefix(p)
        if upstream is not None and i in upstream:
            continue
        if own(p) and chained and upstream is None and ps == 0:
            unresolved_upstream[p].append(i)   # shared A-/Q- may be defined in files we could not load
        elif own(p):
            errors.append(f"{i} is referenced but never defined (line {lines[0]})")
        elif ps is not None and ps < stage:
            if upstream is not None:
                errors.append(f"{i} is referenced (line {lines[0]}) but defined in no upstream document")
            else:
                unresolved_upstream[p].append(i)
        else:
            errors.append(f"{i} is referenced (line {lines[0]}) but belongs to a later stage and is not defined")
    for i, lines in sorted(s.fence_ids.items()):
        if i not in s.defs and not (upstream and i in upstream):
            errors.append(f"{i} appears in a code block (line {lines[0]}) but is never defined")
    if unresolved_upstream:
        n = sum(len(v) for v in unresolved_upstream.values())
        sample = ", ".join(sorted(x for v in unresolved_upstream.values() for x in v)[:4])
        warnings.append(f"{n} upstream-style ID(s) are cited but could not be verified because the earlier documents "
                        f"were not loaded (e.g. {sample}); re-run with --upstream <earlier documents>")

    if gaps:
        by = defaultdict(list)
        for i in s.defs:
            if "-" in i and i.count("-") == 1 and own(prefix_of(i)):
                by[prefix_of(i)].append(number_of(i))
        for p, nums in sorted(by.items()):
            nums.sort()
            if stage_of_prefix(p) == 0 and upstream is not None:
                continue  # A/Q continue after the upstream numbers; contiguity is checked by the chain validator
            exp = list(range(nums[0], nums[0] + len(nums)))
            if nums != exp:
                warnings.append(f"{p}- numbering has gaps: {nums} (fine if an item was removed on purpose)")

    if orphans:
        used = set(s.refs) | set(s.fence_ids)
        for i in sorted(s.defs):
            if prefix_of(i) in orphan_prefixes and i not in used:
                warnings.append(f"{i} is defined but never referenced")
    return errors, warnings


def cli(argv, stage, doc, malformed_is_error=False, gaps=True, orphan_prefixes=()):
    """Shared command-line front end: validate_ids.py <doc.md> [--upstream a.md b.md] [--orphans]."""
    import sys
    from pathlib import Path
    paths, upstream_paths, orphans, mode = [], [], False, "docs"
    for a in argv:
        if a == "--upstream":
            mode = "up"
        elif a == "--orphans":
            orphans, mode = True, "docs"
        elif a.startswith("--"):
            print(doc)
            return 2
        elif mode == "up":
            upstream_paths.append(a)
        else:
            paths.append(a)
    if not paths:
        print(doc)
        return 2
    if upstream_paths:
        missing = [p for p in upstream_paths if not Path(p).exists()]
        if missing:
            print(f"ERROR: upstream file(s) not found: {', '.join(missing)}")
            return 1
    total = 0
    for p in paths:
        path = Path(p)
        if not path.exists():
            print(f"ERROR: {p}: file not found")
            total += 1
            continue
        text = path.read_text(encoding="utf-8")
        upstream, chained, note = auto_upstream(path, text, upstream_paths)
        if note:
            print(f"NOTE: {p}: {note}")
        s = scan(text)
        errors, warnings = check_doc(s, stage, upstream, malformed_is_error, gaps, orphans, orphan_prefixes, chained)
        for w in warnings:
            print(f"WARNING: {p}: {w}")
        for e in errors:
            print(f"ERROR: {p}: {e}")
        print(f"{p}: {len(s.defs)} ID(s) defined, {len(errors)} error(s), {len(warnings)} warning(s)")
        total += len(errors)
    return 1 if total else 0
