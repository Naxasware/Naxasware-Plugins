#!/usr/bin/env python3
"""
Render a structured requirements JSON document (schema in
references/requirement-schema.md) into a deliverable format.

This is a deterministic renderer, not an analysis tool — it assumes you
(the model) have already done the requirements engineering and assembled
the JSON. It exists so formatting a matrix, a CSV, or a clean markdown
summary is mechanical and doesn't risk transcription errors or dropped
rows on a large document.

Usage:
    python generate_report.py <input.json> --format markdown [-o out.md]
    python generate_report.py <input.json> --format csv [-o out.csv]
    python generate_report.py <input.json> --format matrix [-o out.md]

Formats:
    markdown  A readable summary document (requirements, business rules,
              NFRs, open questions, assumptions) grouped by section.
    csv       A flat requirement matrix: id, name, description, actor,
              priority, status, confidence, evidence — one row per
              requirement. Good for spreadsheets / stakeholder review.
    matrix    A markdown traceability matrix using the "traceability" and
              "evidence" arrays: business objective -> requirement ->
              (evidence / status / confidence).

If a section/array is missing from the input JSON it's simply skipped —
this script never invents content, it only formats what's given.
"""

import argparse
import csv
import json
import sys
from io import StringIO


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get(d, *keys, default=""):
    for k in keys:
        if isinstance(d, dict) and k in d and d[k] not in (None, ""):
            return d[k]
    return default


def render_markdown(data):
    out = []
    project = data.get("project", {})
    title = get(project, "name", "title", default="Requirements Document")
    out.append(f"# {title}\n")

    if project.get("description"):
        out.append(f"{project['description']}\n")

    def section(title, items, renderer):
        if not items:
            return
        out.append(f"## {title}\n")
        for item in items:
            out.append(renderer(item))
        out.append("")

    section("Business Objectives", data.get("business_objectives", []),
             lambda o: f"- **{get(o,'id')}** {get(o,'name','description')}\n")

    section("Stakeholders", data.get("stakeholders", []),
             lambda s: f"- **{get(s,'id')}** {get(s,'name')} — {get(s,'interest','role')}\n")

    section("Actors", data.get("actors", []),
             lambda a: f"- **{get(a,'id')}** {get(a,'name')}\n")

    def render_requirement(r):
        lines = [f"### {get(r,'id')} — {get(r,'name')}\n"]
        if r.get("description"):
            lines.append(f"{r['description']}\n")
        meta = []
        for field in ("actor", "priority", "status", "confidence"):
            if r.get(field):
                meta.append(f"**{field.capitalize()}:** {r[field]}")
        if meta:
            lines.append("  \n".join(meta) + "\n")
        evidence = r.get("evidence")
        if evidence:
            ev_str = evidence if isinstance(evidence, str) else ", ".join(evidence)
            lines.append(f"**Evidence:** {ev_str}\n")
        return "\n".join(lines)

    section("Requirements", data.get("requirements", []), render_requirement)

    section("Business Rules", data.get("business_rules", []),
             lambda b: f"- **{get(b,'id')}** {get(b,'description','name')}\n")

    section("Data Requirements", data.get("data_requirements", []),
             lambda d: f"- **{get(d,'id')}** {get(d,'entity','name')}: {get(d,'description')}\n")

    section("Non-Functional Requirements", data.get("non_functional_requirements", []),
             lambda n: f"- **{get(n,'id')}** [{get(n,'category')}] {get(n,'description')}\n")

    section("Integrations", data.get("integrations", []),
             lambda i: f"- **{get(i,'id')}** {get(i,'system','name')}: {get(i,'purpose','description')}\n")

    section("AI Requirements", data.get("ai_requirements", []),
             lambda a: f"- **{get(a,'id')}** {get(a,'description','name')}\n")

    section("Automation Requirements", data.get("automation_requirements", []),
             lambda a: f"- **{get(a,'id')}** {get(a,'description','name')}\n")

    section("Assumptions", data.get("assumptions", []),
             lambda a: f"- **{get(a,'id')}** {get(a,'description')} "
                       f"(impact if wrong: {get(a,'impact_if_incorrect', default='not stated')})\n")

    section("Constraints", data.get("constraints", []),
             lambda c: f"- **{get(c,'id')}** {get(c,'description')}\n")

    section("Dependencies", data.get("dependencies", []),
             lambda d: f"- **{get(d,'id')}** {get(d,'description')}\n")

    section("Open Questions", data.get("open_questions", []),
             lambda q: f"- **{get(q,'id')}** {get(q,'description','question')}\n")

    return "\n".join(out)


def render_csv(data):
    buf = StringIO()
    fieldnames = ["id", "name", "description", "actor", "priority",
                  "status", "confidence", "evidence"]
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for r in data.get("requirements", []):
        evidence = r.get("evidence", "")
        if isinstance(evidence, list):
            evidence = "; ".join(evidence)
        writer.writerow({
            "id": get(r, "id"),
            "name": get(r, "name"),
            "description": get(r, "description"),
            "actor": get(r, "actor"),
            "priority": get(r, "priority"),
            "status": get(r, "status"),
            "confidence": get(r, "confidence"),
            "evidence": evidence,
        })
    return buf.getvalue()


def render_matrix(data):
    out = ["# Traceability Matrix\n"]
    out.append("| Business Objective | Requirement | Status | Confidence | Evidence |")
    out.append("|---|---|---|---|---|")

    req_by_id = {get(r, "id"): r for r in data.get("requirements", [])}
    trace = data.get("traceability", [])

    if trace:
        for t in trace:
            bo = get(t, "business_objective", "bo", default="")
            req_id = get(t, "requirement", "requirement_id", "fr", default="")
            req = req_by_id.get(req_id, {})
            evidence = req.get("evidence", "")
            if isinstance(evidence, list):
                evidence = "; ".join(evidence)
            out.append(f"| {bo} | {req_id} | {get(req,'status')} | "
                       f"{get(req,'confidence')} | {evidence} |")
    else:
        # No explicit traceability array — fall back to one row per requirement.
        for r in data.get("requirements", []):
            evidence = r.get("evidence", "")
            if isinstance(evidence, list):
                evidence = "; ".join(evidence)
            out.append(f"| — | {get(r,'id')} | {get(r,'status')} | "
                       f"{get(r,'confidence')} | {evidence} |")

    return "\n".join(out) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", help="Path to the structured requirements JSON file")
    parser.add_argument("--format", choices=["markdown", "csv", "matrix"], required=True)
    parser.add_argument("-o", "--output", help="Output file path (defaults to stdout)")
    args = parser.parse_args()

    try:
        data = load(args.input)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error reading {args.input}: {e}", file=sys.stderr)
        sys.exit(1)

    if args.format == "markdown":
        rendered = render_markdown(data)
    elif args.format == "csv":
        rendered = render_csv(data)
    else:
        rendered = render_matrix(data)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(rendered)
        print(f"Wrote {args.output}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
