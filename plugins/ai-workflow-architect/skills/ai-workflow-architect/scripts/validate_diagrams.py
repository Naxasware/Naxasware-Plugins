#!/usr/bin/env python3
"""
Check diagrams embedded in a workflow-architecture Markdown document.

Mermaid blocks (```mermaid):
  - first line declares a known diagram type
  - flowchart/graph: balanced () [] {} outside quoted labels, balanced
    subgraph/end, no dangling arrows, decision nodes {..} have >= 2 outgoing
    edges, declared-but-unconnected nodes
  - sequenceDiagram: balanced alt/opt/loop/par/critical/break/rect ... end;
    messages use declared participants when participants are declared
PlantUML blocks (```plantuml): @startuml / @enduml present and balanced.

Consistency with the document: every STEP/DEC/TOOL/TASK/... ID that appears in
a diagram must be defined in the document text (see validate_ids.py).

Limits: this is a lightweight syntax and consistency lint, not a Mermaid
renderer. Edge labels written as `A -- text --> B` are not parsed; use
`A -->|text| B`. Rendering in a real Mermaid viewer is the final check.

Usage:
    python3 validate_diagrams.py architecture.md [--coverage] [--require]

    --coverage  warn about STEP IDs that appear in no diagram
    --require   error if the document contains no diagram at all

Exit code 1 if any error. Standard library only.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_ids as vids  # noqa: E402

MERMAID_TYPES = (
    "flowchart", "graph", "sequenceDiagram", "stateDiagram-v2", "stateDiagram", "classDiagram",
    "erDiagram", "gantt", "journey", "pie", "mindmap", "timeline", "gitGraph", "quadrantChart",
    "requirementDiagram", "C4Context", "C4Container", "C4Component", "C4Dynamic",
    "sankey-beta", "xychart-beta", "block-beta", "architecture-beta",
)
ARROW_RE = re.compile(r"<?(?:-{2,}>|={2,}>|-\.+->|-{2,}[xo]|-{3,}|~{3})")
SKIP_FLOW = ("subgraph", "end", "classdef", "class ", "style ", "linkstyle", "click ", "direction", "%%")
SEQ_OPEN = ("alt ", "opt ", "loop ", "par ", "critical ", "break ", "rect ")
SEQ_MSG_RE = re.compile(r"^\s*([A-Za-z_][\w ]*?)\s*(?:--?>>|--?>|--?x|--?\)|-\))\s*[+-]?([A-Za-z_][\w ]*?)\s*:")


def extract_blocks(text):
    """Return list of (lang, start_line_1based, [lines])."""
    blocks, cur = [], None
    for no, line in enumerate(text.splitlines(), 1):
        st = line.strip()
        if st.startswith("```"):
            if cur is None:
                cur = [st[3:].strip().lower(), no + 1, []]
            else:
                blocks.append(tuple(cur))
                cur = None
        elif cur is not None:
            cur[2].append(line)
    return blocks


def meaningful(lines):
    out, in_front = [], False
    for i, ln in enumerate(lines):
        st = ln.strip()
        if i == 0 and st == "---":
            in_front = True
            continue
        if in_front:
            if st == "---":
                in_front = False
            continue
        if not st or st.startswith("%%"):
            continue
        out.append((i, ln))
    return out


def strip_quotes(s):
    return re.sub(r'"[^"]*"', '""', s)


def shrink_labels(s):
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"\[[^\[\]]*\]|\{[^{}]*\}|\([^()]*\)", "", s)
    return s


def check_flowchart(body, base, where, errors, warnings):
    # bracket balance (ignoring quoted labels)
    joined = strip_quotes("\n".join(l for _, l in body if not l.strip().startswith("%%")))
    for o, c in ("()", "[]", "{}"):
        if joined.count(o) != joined.count(c):
            errors.append(f"{where}: unbalanced '{o}{c}' ({joined.count(o)} vs {joined.count(c)}); check node labels")
    subs = sum(1 for _, l in body if l.strip().startswith("subgraph"))
    ends = sum(1 for _, l in body if l.strip() == "end")
    if subs != ends:
        errors.append(f"{where}: {subs} subgraph(s) but {ends} 'end'(s)")

    decisions, out_edges, connected, declared = set(), {}, set(), {}
    for i, ln in body[1:]:
        st = ln.strip()
        if st.lower().startswith(SKIP_FLOW) or st.lower() == "end":
            continue
        line_no = base + i
        raw = strip_quotes(st)
        for m in re.finditer(r"(?<![\w-])([A-Za-z_]\w*)\{(?!\{)", raw):
            decisions.add(m.group(1))
        flat = shrink_labels(raw)
        flat = re.sub(r"\|[^|]*\|", "", flat)
        flat = re.sub(r":::\w+", "", flat)
        parts = ARROW_RE.split(flat)
        arrows = ARROW_RE.findall(flat)
        if arrows:
            segs = [[n.strip() for n in p.split("&")] for p in parts]
            if any(not any(s) for s in segs):
                errors.append(f"{where} line {line_no}: dangling arrow (missing node on one side)")
                continue
            for k in range(len(segs) - 1):
                for src in segs[k]:
                    out_edges[src] = out_edges.get(src, 0) + len(segs[k + 1])
                    connected.add(src)
                for dst in segs[k + 1]:
                    connected.add(dst)
        else:
            for n in re.findall(r"[A-Za-z_]\w*", flat):
                declared.setdefault(n, line_no)
    for d in sorted(decisions):
        if out_edges.get(d, 0) < 2:
            warnings.append(f"{where}: decision node '{d}' has {out_edges.get(d, 0)} outgoing edge(s); show every branch, including failure")
    for n, ln in sorted(declared.items(), key=lambda kv: kv[1]):
        if n not in connected and n not in decisions and len(connected) > 0:
            warnings.append(f"{where} line {ln}: node '{n}' is declared but not connected to anything")


def check_sequence(body, base, where, errors, warnings):
    depth = 0
    declared = set()
    uses = []
    for i, ln in body[1:]:
        st = ln.strip()
        m = re.match(r"(?:participant|actor)\s+([A-Za-z_]\w*)(?:\s+as\s+.+)?$", st)
        if m:
            declared.add(m.group(1))
            continue
        if st.startswith(SEQ_OPEN):
            depth += 1
        elif st == "end":
            depth -= 1
            if depth < 0:
                errors.append(f"{where} line {base + i}: 'end' without matching block")
                depth = 0
        mm = SEQ_MSG_RE.match(st)
        if mm:
            uses.append((base + i, mm.group(1).strip(), mm.group(2).strip()))
    if depth > 0:
        errors.append(f"{where}: {depth} block(s) (alt/opt/loop/par/...) not closed with 'end'")
    if declared:
        for ln, a, b in uses:
            for who in (a, b):
                if who not in declared:
                    warnings.append(f"{where} line {ln}: '{who}' is not a declared participant")


def check_mermaid(lines, start, idx, errors, warnings):
    where = f"mermaid block #{idx} (line {start})"
    body = meaningful(lines)
    if not body:
        errors.append(f"{where}: empty diagram")
        return
    first = body[0][1].strip()
    dtype = next((t for t in MERMAID_TYPES if first == t or first.startswith(t + " ") or first.startswith(t + "\t")), None)
    if not dtype:
        errors.append(f"{where}: first line '{first[:40]}' is not a known Mermaid diagram type")
        return
    if dtype in ("flowchart", "graph"):
        check_flowchart(body, start, where, errors, warnings)
    elif dtype == "sequenceDiagram":
        check_sequence(body, start, where, errors, warnings)


def check_plantuml(lines, start, idx, errors):
    txt = "\n".join(lines)
    s, e = len(re.findall(r"@start\w+", txt)), len(re.findall(r"@end\w+", txt))
    if s == 0 or s != e:
        errors.append(f"plantuml block #{idx} (line {start}): needs matching @startuml/@enduml (found {s} start, {e} end)")


def main(argv):
    coverage, require = "--coverage" in argv, "--require" in argv
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__)
        return 2
    failed = False
    for p in paths:
        path = Path(p)
        if not path.exists():
            print(f"ERROR: {p}: file not found")
            failed = True
            continue
        text = path.read_text(encoding="utf-8")
        scan_res = vids.scan(text)
        errors, warnings = [], []
        blocks = extract_blocks(text)
        n_diagrams = 0
        for idx, (lang, start, lines) in enumerate(blocks, 1):
            if lang == "mermaid":
                n_diagrams += 1
                check_mermaid(lines, start, n_diagrams, errors, warnings)
            elif lang in ("plantuml", "puml"):
                n_diagrams += 1
                check_plantuml(lines, start, n_diagrams, errors)
        for i, lns in sorted(scan_res.fence_ids.items()):
            if i not in scan_res.defs:
                errors.append(f"{i} appears in a diagram/code block (line {lns[0]}) but is not defined in the document")
        if coverage and n_diagrams:
            for i in sorted(x for x in scan_res.defs if x.startswith("STEP-")):
                if i not in scan_res.fence_ids:
                    warnings.append(f"{i} appears in no diagram")
        if require and n_diagrams == 0:
            errors.append("no diagrams found (expected a ```mermaid or ```plantuml block)")
        for w in warnings:
            print(f"WARNING: {p}: {w}")
        for e in errors:
            print(f"ERROR: {p}: {e}")
        print(f"{p}: {n_diagrams} diagram(s), {len(errors)} error(s), {len(warnings)} warning(s)")
        failed = failed or bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
