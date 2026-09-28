#!/usr/bin/env python3
"""Render a System Architect structured-output JSON file as a Markdown report.

Usage: generate_report.py architecture.json [-o report.md]
Writes to stdout unless -o is given. Credential-like strings are replaced with
[MASKED] so secrets never reach the generated document.
Exit codes: 0 = ok, 2 = usage or I/O problem.
"""
import argparse
import json
import re
import sys

SECRETS = [
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_\-]{32,}\b"),
    re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"),
]
SECTIONS = [
    ("business_context", "Business Context"), ("architecture_drivers", "Architecture Drivers"),
    ("constraints", "Constraints"), ("quality_attributes", "Quality Attributes"),
    ("architecture_options", "Architecture Options"), ("selected_architecture", "Selected Architecture"),
    ("components", "Components"), ("modules", "Modules"), ("data_architecture", "Data Architecture"),
    ("api_architecture", "API Architecture"), ("integration_architecture", "Integration Architecture"),
    ("security_architecture", "Security Architecture"), ("infrastructure", "Infrastructure"),
    ("deployment", "Deployment"), ("observability", "Observability"), ("ai_architecture", "AI Architecture"),
    ("decisions", "Decisions"), ("risks", "Risk Register"), ("assumptions", "Assumptions"),
    ("open_questions", "Open Questions"), ("evidence", "Evidence"), ("traceability", "Traceability"),
]


def mask(s):
    for rx in SECRETS:
        s = rx.sub("[MASKED]", s)
    return s


def scalar(x):
    return not isinstance(x, (dict, list))


def cell(v):
    if isinstance(v, list):
        v = ", ".join(str(i) for i in v)
    elif isinstance(v, dict):
        v = json.dumps(v, ensure_ascii=False)
    elif v is None:
        v = ""
    return mask(str(v)).replace("|", "\\|").replace("\n", " ")


def label(k):
    return str(k).replace("_", " ").strip().capitalize()


def flat_row(d):
    return all(scalar(x) or (isinstance(x, list) and all(scalar(y) for y in x)) for x in d.values())


def render(v, level, out):
    if isinstance(v, dict):
        for k, x in v.items():
            if scalar(x):
                out.append(f"- **{label(k)}:** {cell(x)}")
        for k, x in v.items():
            if not scalar(x) and x:
                out += ["", "#" * min(level, 6) + f" {label(k)}", ""]
                render(x, level + 1, out)
    elif isinstance(v, list):
        if v and all(isinstance(i, dict) and flat_row(i) for i in v):
            cols = []
            for i in v:
                for k in i:
                    if k not in cols:
                        cols.append(k)
            out.append("| " + " | ".join(label(c) for c in cols) + " |")
            out.append("|" + "---|" * len(cols))
            for i in v:
                out.append("| " + " | ".join(cell(i.get(c)) for c in cols) + " |")
        else:
            for i in v:
                if scalar(i):
                    out.append(f"- {cell(i)}")
                else:
                    render(i, level, out)
                    out.append("")
    else:
        out.append(cell(v))


def main():
    ap = argparse.ArgumentParser(description="Render architecture JSON as Markdown.")
    ap.add_argument("input")
    ap.add_argument("-o", "--output")
    a = ap.parse_args()
    try:
        with open(a.input, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Cannot read {a.input}: {e}", file=sys.stderr)
        sys.exit(2)
    proj = data.get("project", {}) if isinstance(data, dict) else {}
    out = [f"# Architecture: {cell(proj.get('name', 'Untitled'))}", ""]
    render({k: v for k, v in proj.items() if k != "name"}, 2, out)
    for key, title in SECTIONS:
        val = data.get(key)
        if val:
            out += ["", f"## {title}", ""]
            render(val, 3, out)
    text = "\n".join(out).rstrip() + "\n"
    if a.output:
        with open(a.output, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
