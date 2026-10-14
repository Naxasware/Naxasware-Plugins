#!/usr/bin/env python3
"""
Summarize a workflow-architecture Markdown document as a short report.

Contents: ID inventory, evidence-tag usage, recommendation classes,
traceability matrix (which WD/STEP/TOOL/TASK/TEST each requirement links to,
by appearing on the same line), assumptions, open questions, risks, and the
result of validate_workflow.py.

Usage:
    python3 generate_report.py architecture.md [-o report.md] [--depth quick|standard|full]

Without --depth, the depth is read from a `Depth: ...` line near the top of the
document (else standard), so the report always matches how the document was written.

Writes to stdout unless -o is given. Exit code 0 even if validation finds
problems (they are reported); 2 on usage errors. Standard library only.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_ids as vids  # noqa: E402
import validate_workflow as vw  # noqa: E402

NAMES = {
    "BO": "Business objectives", "WR": "Requirements", "WD": "Drivers", "STEP": "Steps",
    "DEC": "Decisions", "TOOL": "Tools", "TASK": "Tasks", "TEST": "Tests",
    "WADR": "ADRs", "WRISK": "Risks", "A": "Assumptions", "Q": "Open questions",
}
EVIDENCE = ["STATED", "DOCUMENTED", "OBSERVED", "INFERRED", "ASSUMED", "RECOMMENDED", "UNKNOWN"]
GAPS = ["NOT PROVIDED", "REQUIRES VALIDATION"]
CLASSES = ["REQUIRED", "RECOMMENDED", "OPTIONAL", "FUTURE", "EXPERIMENTAL"]
CLASS_RE = re.compile(r"^\s*(?:[-*+]\s+|\|\s*)?(?:\*\*)?(REQUIRED|RECOMMENDED|OPTIONAL|FUTURE|EXPERIMENTAL)\b")


def cell(text, limit=110):
    text = re.sub(r"\s+", " ", text.replace("|", "/")).strip(" /")
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def describe(sr, i):
    """Readable one-liner for a defined ID: its line without the leading marker and ID."""
    t = sr.def_text.get(i, "")
    t = re.sub(r"^[#>*+\-\s|`]*(?:\*\*)?" + re.escape(i) + r"(?:\*\*|`)?\s*[|:—–-]*\s*", "", t)
    return cell(t)


def explicit_trace(text):
    """Rows of the document's own Traceability table: {WR id: {prefix: [ids]}}.
    Used in preference to same-line links, which also pick up dependency columns
    (a task that merely depends on another task is not an implementation of the requirement)."""
    rows, in_sec, header = {}, False, None
    for line in text.splitlines():
        h = re.match(r"^#{1,6}\s+(.*)$", line)
        if h:
            in_sec, header = bool(re.search(r"traceab", h.group(1), re.I)), None
            continue
        if not in_sec or not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or re.match(r"^[-: ]+$", cells[0]):
            continue
        if not re.match(r"^`?WR-\d+", cells[0]):
            header = [c.strip("` *").upper() for c in cells]
            continue
        if header:
            wr = re.match(r"`?(WR-\d+)", cells[0]).group(1)
            d = {}
            for name, val in zip(header, cells):
                for p in ("WD", "STEP", "TOOL", "TASK", "TEST"):
                    if name.startswith(p):
                        d.setdefault(p, [])
                        d[p] += re.findall(rf"\b{p}-\d+\b", val)
            rows[wr] = d
    return rows


def build(text, depth, upstream=None, chained=False):
    sr = vids.scan(text)
    errors, warnings = vw.validate(text, depth, upstream=upstream, chained=chained)
    lines = text.splitlines()
    title = next((re.sub(r"^#\s+", "", l).strip() for l in lines if re.match(r"^#\s+", l)), "Workflow architecture")
    out = [f"# Report: {title}", "", f"Depth checked: **{depth}** · Validation: **{len(errors)} error(s), {len(warnings)} warning(s)**", ""]

    out += ["## ID inventory", "", "| Prefix | Kind | Defined |", "|---|---|---|"]
    for p in vids.PREFIXES:
        n = sum(1 for i in sr.defs if i.split("-")[0] == p)
        if n:
            out.append(f"| `{p}` | {NAMES[p]} | {n} |")
    out.append("")

    body = vw.strip_fences(text)
    ev = [(t, len(re.findall(r"\[" + t + r"\]", body))) for t in EVIDENCE]
    ev += [(g, len(re.findall(r"\b" + g + r"\b", body))) for g in GAPS]
    ev = [(t, n) for t, n in ev if n]
    out += ["## Evidence and gaps", ""]
    out.append(", ".join(f"{t}: {n}" for t, n in ev) if ev else "No evidence tags found — facts are not labeled.")
    out.append("")

    cls = {c: 0 for c in CLASSES}
    for l in lines:
        m = CLASS_RE.match(l)
        if m:
            cls[m.group(1)] += 1
    if any(cls.values()):
        out += ["## Recommendations by class", "", ", ".join(f"{c}: {n}" for c, n in cls.items() if n), ""]

    graph = vw.build_graph(sr)
    wrs = sorted(i for i in sr.defs if i.startswith("WR-"))
    explicit = explicit_trace(text)
    if wrs:
        title = "Traceability (from the document's own table)" if explicit else "Traceability (same-line links)"
        out += [f"## {title}", "", "| WR | WD | STEP | TOOL | TASK | TEST |", "|---|---|---|---|---|---|"]
        for w in wrs:
            row = [w]
            for p in ("WD", "STEP", "TOOL", "TASK", "TEST"):
                if w in explicit and p in explicit[w]:
                    linked = sorted(set(explicit[w][p]))
                else:
                    linked = sorted(x for x in graph.get(w, ()) if x.startswith(p + "-"))
                row.append(", ".join(linked) or "—")
            out.append("| " + " | ".join(row) + " |")
        out.append("")

    for prefix, heading in (("A", "Assumptions"), ("Q", "Open questions"), ("WRISK", "Risks")):
        ids = sorted(i for i in sr.defs if i.split("-")[0] == prefix)
        if ids:
            out += [f"## {heading}", ""] + [f"- **{i}** — {describe(sr, i)}" for i in ids] + [""]

    out += ["## Validation findings", ""]
    if not errors and not warnings:
        out.append("None.")
    out += [f"- ERROR: {e}" for e in errors] + [f"- WARNING: {w}" for w in warnings]
    out.append("")
    return "\n".join(out)


def main(argv):
    depth, outfile, path, it = None, None, None, iter(argv)
    for a in it:
        if a == "-o":
            outfile = next(it, None)
        elif a == "--depth":
            depth = next(it, "")
        elif not a.startswith("-"):
            path = a
    if not path or not Path(path).exists() or (depth is not None and depth not in vw.DEPTHS):
        print(__doc__)
        return 2
    text = Path(path).read_text(encoding="utf-8")
    upstream, chained, _ = vids.idscan.auto_upstream(path, text)
    report = build(text, depth or vw.detect_depth(text), upstream, chained)
    if outfile:
        Path(outfile).write_text(report, encoding="utf-8")
        print(f"Wrote {outfile}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
