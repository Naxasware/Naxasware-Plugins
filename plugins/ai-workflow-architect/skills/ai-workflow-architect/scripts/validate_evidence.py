#!/usr/bin/env python3
"""Validate an evidence / drift / review report for an existing workflow.

Checks (standard library only):
  - evidence tables: a header with "Evidence Type" and "Confidence" columns; every
    row uses a valid evidence type and a valid confidence; INFERRED, ASSUMED and
    RECOMMENDED rows may not be HIGH confidence
  - DRIFT-### records: each defined once, with all seven fields (Drift, Expected,
    Observed, Evidence, Impact, Risk, Recommended Action); Recommended Action starts
    with a valid class
  - recommendation classes in "Class:" style lines are valid
  - unmasked secrets (key=value pairs with secret-looking names and real values,
    well-known token formats)
Warns when a report has no evidence table and no DRIFT record.

Usage: python3 validate_evidence.py report.md [more.md ...] [--strict]
Exit codes: 0 ok, 1 errors (or warnings with --strict), 2 usage error.
"""
import re
import sys
from pathlib import Path

TYPES = {"USER_STATED", "DOCUMENTED", "WORKFLOW_OBSERVED", "CODE_OBSERVED", "CONFIG_OBSERVED",
         "DATABASE_OBSERVED", "API_OBSERVED", "INFRASTRUCTURE_OBSERVED", "MONITORING_OBSERVED",
         "PROJECT_TRACKER_OBSERVED", "INFERRED", "ASSUMED", "RECOMMENDED", "UNKNOWN"}
LOW_ONLY = {"INFERRED", "ASSUMED", "RECOMMENDED"}
CONF = {"HIGH", "MEDIUM", "LOW", "UNKNOWN"}
CLASSES = {"REQUIRED", "RECOMMENDED", "OPTIONAL", "FUTURE", "EXPERIMENTAL"}
DRIFT_FIELDS = ["Drift", "Expected", "Observed", "Evidence", "Impact", "Risk", "Recommended Action"]
DRIFT_HEAD = re.compile(r"^(?:#{1,6}\s+|[-*]\s+|\|\s*)?\*{0,2}(DRIFT-\d{3})\b")
SECRET_NAME = r"(?:api[_-]?key|secret|token|password|passwd|private[_-]?key|client[_-]?secret|access[_-]?key)"
SECRET_KV = re.compile(r"\b[A-Za-z0-9_.-]*" + SECRET_NAME + r"[A-Za-z0-9_.-]*\s*[:=]\s*[\"']?([^\s\"'|,;`]+)", re.I)
SECRET_FMT = [re.compile(p) for p in (
    r"\bgh[pousr]_[A-Za-z0-9]{36,}\b", r"\bAKIA[0-9A-Z]{16}\b",
    r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    r"\bsk-(?:ant-)?[A-Za-z0-9_\-]{32,}\b", r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")]
SAFE_VALUE = re.compile(r"^(?:\*+|x{3,}|<[^>]*>|\$\{[^}]*\}|\{\{[^}]*\}\}|\[?redacted\]?|masked|none|null|n/a|"
                        r"unknown|set|present|absent|missing|required|stored|referenced|\.\.\.|…)$", re.I)


def cells(line):
    return [c.strip().strip("`*") for c in line.strip().strip("|").split("|")]


def check(path):
    errs, warns = [], []
    lines = path.read_text(encoding="utf-8").splitlines()
    in_fence = False
    cols = None
    drift_ids, ev_rows = {}, 0
    current = None  # (id, line_no, text)
    blocks = []
    for n, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # secrets
        for m in SECRET_KV.finditer(line):
            v = m.group(1).strip("`*.,)")
            if v and not SAFE_VALUE.match(v) and len(v) >= 8:
                errs.append(f"{path.name}:{n}: possible unmasked secret value ({m.group(0)[:30]}...)")
        for rx in SECRET_FMT:
            if rx.search(line):
                errs.append(f"{path.name}:{n}: secret-like token or key block")
        # evidence tables
        if line.lstrip().startswith("|"):
            c = cells(line)
            low = [x.lower() for x in c]
            if "evidence type" in low and "confidence" in low:
                cols = {name: low.index(name) for name in ("evidence type", "confidence")}
                continue
            if cols is not None:
                if set("".join(c)) <= set("-: "):
                    continue
                if max(cols.values()) < len(c):
                    ev_rows += 1
                    et = c[cols["evidence type"]].upper()
                    cf = c[cols["confidence"]].upper()
                    if et not in TYPES:
                        errs.append(f"{path.name}:{n}: invalid evidence type '{c[cols['evidence type']]}'")
                    if cf not in CONF:
                        errs.append(f"{path.name}:{n}: invalid confidence '{c[cols['confidence']]}'")
                    elif cf == "HIGH" and et in LOW_ONLY:
                        errs.append(f"{path.name}:{n}: {et} evidence cannot be HIGH confidence")
                continue
        else:
            cols = None
        m = DRIFT_HEAD.match(line.strip())
        if m and (line.lstrip().startswith(("#", "-", "*", "|")) or line.startswith("DRIFT-")):
            if line.lstrip().startswith("|") and "drift" in line.lower() and m.group(1) in drift_ids:
                pass
            did = m.group(1)
            is_def = line.lstrip().startswith("#") or line.lstrip().startswith(("-", "*")) is False
            if line.lstrip().startswith("#"):
                if did in drift_ids:
                    errs.append(f"{path.name}:{n}: {did} defined twice (first at line {drift_ids[did]})")
                drift_ids[did] = n
                current = [did, n, []]
                blocks.append(current)
                continue
        if current is not None:
            if re.match(r"^#{1,6}\s", line):
                current = None
            else:
                current[2].append(line)
        cm = re.match(r"^\s*[-*]?\s*\**(?:Class|Classification)\**\s*:\s*\**([A-Za-z_]+)", line)
        if cm and cm.group(1).upper() not in CLASSES:
            errs.append(f"{path.name}:{n}: invalid recommendation class '{cm.group(1)}'")
    for did, n, body in blocks:
        text = "\n".join(body)
        for f in DRIFT_FIELDS:
            if not re.search(r"^\s*(?:[-*]\s*)?\**" + re.escape(f) + r"\**\s*:\**\s*\S", text, re.I | re.M):
                errs.append(f"{path.name}:{n}: {did} is missing field '{f}' (or it is empty)")
        am = re.search(r"Recommended Action\**\s*:\**\s*\**([A-Za-z_]+)", text, re.I)
        if am and am.group(1).upper() not in CLASSES:
            errs.append(f"{path.name}:{n}: {did} Recommended Action must start with one of {sorted(CLASSES)}")
    if not drift_ids and ev_rows == 0:
        warns.append(f"{path.name}: no evidence table and no DRIFT record found")
    return errs, warns


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    strict = "--strict" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(2)
    all_e, all_w = [], []
    for a in args:
        p = Path(a)
        if not p.is_file():
            print(f"error: {a} not found")
            sys.exit(2)
        e, w = check(p)
        all_e += e
        all_w += w
    for e in all_e:
        print("ERROR:", e)
    for w in all_w:
        print("WARNING:", w)
    if not all_e and not all_w:
        print("validate_evidence: OK")
    sys.exit(1 if all_e or (strict and all_w) else 0)


if __name__ == "__main__":
    main()
