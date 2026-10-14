#!/usr/bin/env python3
"""Validate a System Architect structured-output JSON file (schema 1.1; 1.0 files still pass).

Usage: validate_architecture.py architecture.json [--upstream 01-requirements.md ...] [--strict]
Checks: required sections, evidence types and confidence values, recommendation
classes, component origin/evidence rules, ID uniqueness and references, risk
fields, numeric scoring (discouraged), and unmasked secrets.

With --upstream (the requirements document(s) this architecture is built from; also
read automatically from project.chain.upstream when the files sit next to the JSON):
  - every requirement ID the architecture cites must be defined upstream (a typo or
    an invented requirement is an error)
  - every Must requirement and every item under the upstream Handoff "Must cover"
    must be covered (error) and every other upstream FR/NFR/BR/AIR/IR/CON/DEP should
    be cited (warning); locked decisions must be cited
  - IDs defined here must not restate an upstream ID; new A-/Q- numbers continue
    after the highest upstream number
In chain mode (project.chain present) a `handoff` section is expected.
--strict turns warnings into errors.
Exit codes: 0 = no errors (warnings allowed), 1 = errors found, 2 = usage or I/O problem.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

EVIDENCE_TYPES = {
    "USER_STATED", "DOCUMENTED", "CODE_OBSERVED", "CONFIG_OBSERVED", "DATABASE_OBSERVED",
    "API_OBSERVED", "INFRASTRUCTURE_OBSERVED", "PROJECT_TRACKER_OBSERVED",
    "MONITORING_OBSERVED", "INFERRED", "ASSUMED", "RECOMMENDED",
}
NON_OBSERVED = {"USER_STATED", "INFERRED", "ASSUMED", "RECOMMENDED"}
CONFIDENCE = {"High", "Medium", "Low", "Unknown"}
CLASSES = {"REQUIRED", "RECOMMENDED", "OPTIONAL", "FUTURE", "EXPERIMENTAL"}
ORIGINS = {"observed", "stated", "recommended", "assumed", "unknown"}
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


STRICT = False
KNOWN_TOP = {"project", "business_context", "selected_architecture", "data_architecture", "api_architecture",
             "integration_architecture", "security_architecture", "infrastructure", "deployment", "observability",
             "ai_architecture", "architecture_drivers", "constraints", "quality_attributes", "architecture_options",
             "components", "modules", "decisions", "risks", "assumptions", "open_questions", "evidence",
             "traceability", "handoff", "carried_forward", "upstream_coverage"}
COVER_PREFIXES = ("FR", "NFR", "BR", "AIR", "IR", "CON", "DEP")


def _ids_from(v):
    import validate_chain as vc
    if isinstance(v, str):
        return vc.ids_in(v)
    if isinstance(v, list):
        out = set()
        for x in v:
            out |= _ids_from(x)
        return out
    return set()


def _must_ids(text):
    """IDs a requirements document marks Must (block 'Priority: Must' or a table row with a Must cell)."""
    out, cur = set(), None
    for line in text.splitlines():
        m = re.match(r"^\s*(?:[#>*-]+\s*)?\**\s*((?:FR|NFR|BR|AIR|IR)-\d{3,4})\b", line)
        if m:
            cur = m.group(1)
        if cur and re.search(r"priority\W{0,3}\s*:?\s*\**\s*must\b", line, re.I):
            out.add(cur)
        r = re.match(r"^\s*\|\s*((?:FR|NFR|BR|AIR|IR)-\d{3,4})\s*\|", line)
        if r and re.search(r"\|\s*must\s*\|", line, re.I):
            out.add(r.group(1))
    return out


def chain_checks(data, json_path, upstream_paths):
    import idscan
    import validate_chain as vc
    proj = data.get("project") or {}
    chain = proj.get("chain")
    handoff = data.get("handoff")

    for k in data:
        if k not in KNOWN_TOP:
            warn(f"unknown top-level section '{k}' (the report renders it under its own heading; "
                 f"schema sections are listed in references/output-schema.md)")

    # IDs this document defines
    own = {}
    for k in ("architecture_drivers", "constraints", "components", "decisions", "risks", "assumptions",
              "open_questions", "architecture_options", "evidence"):
        for it in data.get(k) or []:
            if isinstance(it, dict) and isinstance(it.get("id"), str):
                own.setdefault(it["id"], k)
    integ = data.get("integration_architecture") or {}
    for it in integ.get("interfaces") or []:
        if isinstance(it, dict) and isinstance(it.get("id"), str):
            own.setdefault(it["id"], "interfaces")
    for k in integ:
        if ID_LIKE.match(str(k)):
            own.setdefault(str(k), "integration_architecture")
    for kind, prefix in (("assumptions", "A"), ("open_questions", "Q")):
        for i, it in enumerate(data.get(kind) or []):
            if isinstance(it, dict):
                v = it.get("id", "")
                if v and not re.match(rf"^{prefix}-\d{{3,}}$", v):
                    err(f"{kind}[{i}]: id '{v}' must look like {prefix}-NNN")
            elif chain:
                warn(f"{kind}[{i}] is plain text; in a chain give it an id ({prefix}-NNN) so numbering can continue")

    # upstream documents
    paths = list(upstream_paths)
    if not paths and chain:
        names = chain.get("upstream") or []
        names = [names] if isinstance(names, str) else names
        found = [Path(json_path).resolve().parent / n for n in names if n and n != "none"]
        paths = [str(f) for f in found if f.exists()]
        if names and not paths and names != ["none"]:
            warn("project.chain.upstream names files that were not found next to the JSON; "
                 "upstream citations are not verified (pass --upstream)")
    texts = [Path(p).read_text(encoding="utf-8") for p in paths]
    scans = [idscan.scan(x) for x in texts]
    up_defs = set()
    for s in scans:
        up_defs |= set(s.defs)

    cited = set()
    for d in data.get("architecture_drivers") or []:
        if isinstance(d, dict):
            cited |= _ids_from(d.get("requirement_ids"))
    for r in data.get("traceability") or []:
        if isinstance(r, dict):
            cited |= _ids_from(r.get("requirement"))
    for c in data.get("upstream_coverage") or []:
        if isinstance(c, dict):
            cited |= _ids_from(c.get("upstream"))
            st = str(c.get("status", "")).lower()
            if st in ("deferred", "out of scope", "not applicable") and not c.get("reason"):
                err(f"upstream_coverage: {c.get('upstream')} is '{c.get('status')}' but gives no reason")
    anywhere = vc.ids_in(json.dumps(data, ensure_ascii=False))

    if handoff is None and chain and (chain.get("next") not in (None, "none")):
        warn("chain mode but no 'handoff' section (next_skill, must_cover, locked_decisions, "
             "blocking_questions, next_a, next_q)")
    if isinstance(handoff, dict):
        for k in ("must_cover", "locked_decisions", "blocking_questions", "next_a", "next_q"):
            if k not in handoff:
                warn(f"handoff: missing '{k}'")

    if not texts:
        return
    for oid, kind in own.items():
        if oid in up_defs:
            err(f"{kind}: '{oid}' is already defined upstream; cite it instead of restating it "
                f"(use a different id for your own item and put the upstream id in a 'cites' or 'upstream' field)")

    owned1 = set(idscan.OWNED.get(1, []))
    for c in sorted(cited):
        if idscan.prefix_of(c) in owned1 and c not in up_defs:
            err(f"cites {c}, which no upstream document defines (typo or invented requirement)")

    must = set()
    locked = set()
    blocking = set()
    for x in texts:
        must |= _must_ids(x)
        h = vc.parse_handoff(x) or {}
        must |= vc.ids_in(h.get("must", ""))
        locked |= vc.ids_in(h.get("locked", ""))
        blocking |= vc.ids_in(h.get("blocking", ""))
    for m in sorted(must):
        if m not in up_defs:
            continue
        if m in cited:
            continue
        if m in anywhere:
            msg = f"Must item {m} is mentioned only in prose; add it to traceability or upstream_coverage"
            if chain or str(proj.get("schema_version", "")).startswith("1.1"):
                err(msg)
            else:
                warn(msg)
        else:
            err(f"Must item {m} is not covered: no driver, traceability row or upstream_coverage entry cites it")
    for l in sorted(locked):
        if l not in anywhere:
            err(f"locked decision {l} is not cited anywhere; honour it or challenge it openly in a decision and a question")
    missing = sorted(i for i in up_defs if idscan.prefix_of(i) in COVER_PREFIXES and "-" in i
                     and i.count("-") == 1 and i not in anywhere and i not in must)
    if missing:
        warn("upstream items never cited (cover, defer or mark out of scope): " + ", ".join(missing[:12])
             + (f" (+{len(missing) - 12} more)" if len(missing) > 12 else ""))
    for b in sorted(blocking):
        if b not in anywhere:
            warn(f"upstream blocking question {b} is not carried forward")

    for pre in ("A", "Q"):
        up_nums = [idscan.number_of(i) for i in up_defs if idscan.prefix_of(i) == pre]
        mine = [idscan.number_of(i) for i in own if idscan.prefix_of(i) == pre]
        if up_nums and mine and min(mine) <= max(up_nums):
            warn(f"new {pre}- numbers should continue after {pre}-{max(up_nums):03d}; found {pre}-{min(mine):03d}")
        if isinstance(handoff, dict):
            want = str(handoff.get("next_" + pre.lower(), "")).strip()
            if want.isdigit() and mine and int(want) <= max(mine):
                warn(f"handoff next_{pre.lower()} is {want} but {pre}-{max(mine):03d} is already used")

    if isinstance(handoff, dict):
        for k in ("must_cover", "locked_decisions", "blocking_questions"):
            for i in sorted(_ids_from(handoff.get(k))):
                if i not in up_defs and i not in own:
                    err(f"handoff.{k} lists {i}, which is defined in no document")


def main():
    global STRICT
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(2)
    STRICT = "--strict" in args
    json_path, upstream, mode = None, [], None
    for a in args:
        if a == "--strict":
            continue
        if a == "--upstream":
            mode = "up"
        elif mode == "up":
            upstream.append(a)
        elif json_path is None:
            json_path = a
        else:
            print(__doc__)
            sys.exit(2)
    if json_path is None:
        print(__doc__)
        sys.exit(2)
    try:
        with open(json_path, encoding="utf-8") as f:
            raw = f.read()
        data = json.loads(raw)
        for u in upstream:
            if not Path(u).exists():
                raise OSError(f"upstream file not found: {u}")
    except (OSError, json.JSONDecodeError) as e:
        print(f"Cannot read/parse {json_path}: {e}")
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
        if o == "stated" and not refs:
            warn(f"component {cid}: origin 'stated' (told by the user or a document) should cite evidence_ids")
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
    chain_checks(data, json_path, upstream)
    finish()


def finish():
    print(f"ERRORS ({len(errors)}):" if errors else "No errors.")
    for e in errors:
        print(f"  - {e}")
    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")
    sys.exit(1 if errors or (STRICT and warnings) else 0)


if __name__ == "__main__":
    main()
