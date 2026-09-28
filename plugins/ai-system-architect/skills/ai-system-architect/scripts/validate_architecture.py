#!/usr/bin/env python3
"""Validate a System Architect structured-output JSON file (schema 1.0).

Usage: validate_architecture.py architecture.json
Checks: required sections, evidence types and confidence values, recommendation
classes, component origin/evidence rules, ID uniqueness and references, risk
fields, numeric scoring (discouraged), and unmasked secrets.
Exit codes: 0 = no errors (warnings allowed), 1 = errors found, 2 = usage or I/O problem.
"""
import json
import re
import sys

EVIDENCE_TYPES = {
    "USER_STATED", "DOCUMENTED", "CODE_OBSERVED", "CONFIG_OBSERVED", "DATABASE_OBSERVED",
    "API_OBSERVED", "INFRASTRUCTURE_OBSERVED", "PROJECT_TRACKER_OBSERVED",
    "MONITORING_OBSERVED", "INFERRED", "ASSUMED", "RECOMMENDED",
}
NON_OBSERVED = {"USER_STATED", "INFERRED", "ASSUMED", "RECOMMENDED"}
CONFIDENCE = {"High", "Medium", "Low", "Unknown"}
CLASSES = {"REQUIRED", "RECOMMENDED", "OPTIONAL", "FUTURE", "EXPERIMENTAL"}
ORIGINS = {"observed", "recommended", "assumed", "unknown"}
FITNESS = {"Covered", "Partially Covered", "Not Covered", "Unknown"}
DEBT = {"Confirmed", "Likely", "Potential"}
DICT_KEYS = ["project", "business_context", "selected_architecture", "data_architecture",
             "api_architecture", "integration_architecture", "security_architecture",
             "infrastructure", "deployment", "observability", "ai_architecture"]
LIST_KEYS = ["architecture_drivers", "constraints", "quality_attributes", "architecture_options",
             "components", "modules", "decisions", "risks", "assumptions", "open_questions",
             "evidence", "traceability"]
RISK_FIELDS = ["risk", "impact", "likelihood", "mitigation", "affected_component"]
SECRET_PATTERNS = [
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_\-]{32,}\b"),
    re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"),
]
SECRET_KEY = re.compile(r"(password|passwd|secret|token|api[_-]?key|private[_-]?key|access[_-]?key)", re.I)
MASKED = re.compile(r"^(\*+|<.*>|\[.*\]|\$\{.*\}|\(.*\)|(?-i:[A-Z][A-Z0-9_]*)|redacted|masked)$", re.I)
SCORE_KEYS = {"score", "rating", "points"}
ID_LIKE = re.compile(r"^[A-Z]+-\d+")

errors, warnings = [], []


def err(m):
    errors.append(m)


def warn(m):
    warnings.append(m)


def ids_of(items, label):
    seen = {}
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            err(f"{label}[{i}]: must be an object")
            continue
        v = it.get("id")
        if not v:
            err(f"{label}[{i}]: missing 'id'")
        elif v in seen:
            err(f"{label}: duplicate id '{v}'")
        else:
            seen[v] = it
    return seen


def walk(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            p = f"{path}.{k}" if path else k
            if isinstance(v, (int, float)) and not isinstance(v, bool) and k.lower() in SCORE_KEYS:
                warn(f"{p}: numeric score; use Covered / Partially Covered / Not Covered / Unknown instead")
            if isinstance(v, str) and SECRET_KEY.search(k):
                s = v.strip()
                if len(s) >= 12 and " " not in s and not MASKED.match(s):
                    err(f"{p}: looks like an unmasked secret value; mask or omit it")
            walk(v, p)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f"{path}[{i}]")


def main():
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(2)
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            raw = f.read()
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Cannot read/parse {sys.argv[1]}: {e}")
        sys.exit(2)
    if not isinstance(data, dict):
        print("Top level must be a JSON object")
        sys.exit(2)

    for k in DICT_KEYS:
        if k not in data:
            err(f"missing section '{k}' (use {{}} if not applicable)")
        elif not isinstance(data[k], dict):
            err(f"section '{k}' must be an object")
    for k in LIST_KEYS:
        if k not in data:
            err(f"missing section '{k}' (use [] if not applicable)")
        elif not isinstance(data[k], list):
            err(f"section '{k}' must be an array")
    if errors:
        return finish()

    if not data["project"].get("schema_version"):
        warn("project.schema_version missing")
    for pat in SECRET_PATTERNS:
        if pat.search(raw):
            err("file contains a credential-like string; remove or mask it")
            break
    walk(data)

    ev = ids_of(data["evidence"], "evidence")
    for eid, e in ev.items():
        types = e.get("types") or [t.strip() for t in str(e.get("type", "")).split("+") if t.strip()]
        if not types:
            err(f"evidence {eid}: missing 'types'")
        for t in types:
            if t not in EVIDENCE_TYPES:
                err(f"evidence {eid}: unknown evidence type '{t}'")
        if any(t in EVIDENCE_TYPES and t not in NON_OBSERVED for t in types) and not e.get("sources"):
            err(f"evidence {eid}: observed/documented evidence needs non-empty 'sources'")
        c = e.get("confidence")
        if c is None:
            warn(f"evidence {eid}: no confidence given")
        elif c not in CONFIDENCE:
            err(f"evidence {eid}: confidence '{c}' not in {sorted(CONFIDENCE)}")

    comps = ids_of(data["components"], "components")
    names = {c.get("name") for c in comps.values()}
    for cid, c in comps.items():
        if not c.get("name"):
            err(f"component {cid}: missing 'name'")
        o = c.get("origin")
        if o not in ORIGINS:
            err(f"component {cid}: 'origin' must be one of {sorted(ORIGINS)}")
        refs = c.get("evidence_ids") or []
        if o == "observed" and not refs:
            err(f"component {cid}: origin 'observed' requires evidence_ids")
        for r in refs:
            if r not in ev:
                err(f"component {cid}: evidence_id '{r}' not found")
        if c.get("classification") and c["classification"] not in CLASSES:
            err(f"component {cid}: classification '{c['classification']}' invalid")

    drivers = ids_of(data["architecture_drivers"], "architecture_drivers")
    decs = ids_of(data["decisions"], "decisions")
    for did, d in decs.items():
        if not d.get("title"):
            err(f"decision {did}: missing 'title'")
        if d.get("classification") not in CLASSES:
            err(f"decision {did}: 'classification' must be one of {sorted(CLASSES)}")
        if d.get("confidence") and d["confidence"] not in CONFIDENCE:
            err(f"decision {did}: confidence invalid")
        if d.get("driver") and d["driver"] not in drivers:
            warn(f"decision {did}: driver '{d['driver']}' not in architecture_drivers")
        for c in d.get("components", []) or []:
            if c not in comps:
                warn(f"decision {did}: component '{c}' not in components")

    risks = ids_of(data["risks"], "risks")
    for rid, r in risks.items():
        for f in RISK_FIELDS:
            if not r.get(f):
                err(f"risk {rid}: missing '{f}'")
        ac = r.get("affected_component")
        if ac and ac not in comps and ac not in names:
            warn(f"risk {rid}: affected_component '{ac}' not found")

    for i, q in enumerate(data["quality_attributes"]):
        if isinstance(q, dict) and q.get("status") and q["status"] not in FITNESS:
            err(f"quality_attributes[{i}]: status must be one of {sorted(FITNESS)}")
    for i, opt in enumerate(data["architecture_options"]):
        if isinstance(opt, dict) and opt.get("debt_category") and opt["debt_category"] not in DEBT:
            err(f"architecture_options[{i}]: debt_category must be one of {sorted(DEBT)}")

    known = {"driver": drivers, "decision": decs, "component": comps}
    for i, t in enumerate(data["traceability"]):
        if not isinstance(t, dict):
            err(f"traceability[{i}]: must be an object")
            continue
        for k, pool in known.items():
            v = t.get(k)
            if isinstance(v, str) and ID_LIKE.match(v) and v not in pool:
                warn(f"traceability[{i}]: {k} '{v}' not found")
    finish()


def finish():
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
