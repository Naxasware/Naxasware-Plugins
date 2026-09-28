#!/usr/bin/env python3
"""Check that diagram components and architecture components agree.

Usage: validate_diagrams.py architecture.json diagram [diagram ...]
Diagram files: .mmd/.mermaid (Mermaid), .puml/.plantuml/.pu (PlantUML), or .md with
fenced ```mermaid / ```plantuml blocks. A diagram node matches a component when its
label or node id equals the component's name or id (case and punctuation ignored).
A component may set "diagram_exempt": true to skip the missing-from-diagram check.
Diagram node not in architecture -> ERROR (undocumented component).
Architecture component in no diagram -> WARNING (diagrams may be partial).
Exit codes: 0 = no errors, 1 = errors found, 2 = usage or I/O problem.
"""
import json
import re
import sys
from pathlib import Path

FENCE = re.compile(r"```(mermaid|plantuml)\s*\n(.*?)```", re.S | re.I)
MM_SKIP = re.compile(r"^\s*(graph|flowchart|subgraph|end\b|classDef|class\b|style|linkStyle|click|direction|%%|title|sequenceDiagram|C4\w*)", re.I)
MM_NODE = re.compile(r"(?<![\w])([A-Za-z_]\w*)\s*(?:\[\[|\[\(|\(\(|\[|\(|\{\{|\{)\s*(\"[^\"]*\"|[^\]\)\}\"]+)")
MM_SEQ = re.compile(r"^\s*(?:participant|actor)\s+(\w+)(?:\s+as\s+(.+))?$", re.I)
MM_C4 = re.compile(r"^\s*(?:Person|System|SystemDb|SystemQueue|Container|ContainerDb|ContainerQueue|Component)\w*\(\s*(\w+)\s*,\s*\"([^\"]+)\"")
PU_NODE = re.compile(r"^\s*(?:component|database|node|actor|queue|cloud|rectangle|storage|participant|artifact|interface|boundary|control|entity|collections|frame)\s+(\"[^\"]+\"|\[[^\]]+\]|\w+)(?:\s+as\s+(\w+))?", re.I)


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def clean(label):
    label = re.sub(r"<[^>]+>", " ", label.strip().strip('"'))
    return label.strip("[]() ").strip()


def mermaid_nodes(text):
    out = []
    for line in text.splitlines():
        line = re.sub(r"\|[^|\n]*\|", "", line)
        m = MM_SEQ.match(line)
        if m:
            out.append((m.group(1), clean(m.group(2) or m.group(1))))
            continue
        m = MM_C4.match(line)
        if m:
            out.append((m.group(1), m.group(2)))
            continue
        if MM_SKIP.match(line):
            continue
        for m in MM_NODE.finditer(line):
            out.append((m.group(1), clean(m.group(2))))
    return out


def plantuml_nodes(text):
    out = []
    for line in text.splitlines():
        m = PU_NODE.match(line)
        if m:
            label = clean(m.group(1))
            out.append((m.group(2) or label, label))
    return out


def extract(path):
    text = path.read_text(encoding="utf-8")
    ext = path.suffix.lower()
    blocks = []
    if ext in (".mmd", ".mermaid"):
        blocks = [("mermaid", text)]
    elif ext in (".puml", ".plantuml", ".pu"):
        blocks = [("plantuml", text)]
    else:
        blocks = [(k.lower(), b) for k, b in FENCE.findall(text)]
    nodes = []
    for kind, body in blocks:
        nodes += mermaid_nodes(body) if kind == "mermaid" else plantuml_nodes(body)
    return nodes


def main():
    if len(sys.argv) < 3 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(2)
    try:
        arch = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        comps = arch.get("components", [])
        files = [Path(p) for p in sys.argv[2:]]
        diagram_nodes = {str(f): extract(f) for f in files}
    except (OSError, json.JSONDecodeError, AttributeError) as e:
        print(f"Cannot read inputs: {e}")
        sys.exit(2)

    keys = {}
    for c in comps:
        if isinstance(c, dict):
            for k in (c.get("id"), c.get("name")):
                if k:
                    keys[norm(k)] = c
    errors, warnings, matched = [], [], set()
    for f, nodes in diagram_nodes.items():
        if not nodes:
            warnings.append(f"{f}: no diagram nodes recognized (unsupported diagram type?)")
        for node_id, label in nodes:
            hit = keys.get(norm(label)) or keys.get(norm(node_id))
            if hit:
                matched.add(id(hit))
            else:
                errors.append(f"{f}: diagram contains undocumented component '{label}'")
    for c in comps:
        if isinstance(c, dict) and id(c) not in matched and not c.get("diagram_exempt"):
            warnings.append(f"architecture contains component missing from diagrams: {c.get('id')} '{c.get('name')}'")

    print(f"ERRORS ({len(errors)}):" if errors else "No errors.")
    for e in errors:
        print(f"  - {e}")
    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
