#!/usr/bin/env python3
"""
Validate a workflow-architecture Markdown document.

Checks (see references/output-schema.md for the expected structure):
  - ID problems (duplicates, dangling, malformed) via validate_ids.py
  - required sections for the chosen depth (quick | standard | full); a section
    may say "Not applicable: <reason>" instead of having content
  - step coverage: each STEP needs failure behavior, retry and timeout
  - traceability: requirements reach a step/task; at full depth, tasks reach a test
  - unlabeled figures anywhere in the document: money, percentages, volumes
    (each must carry an evidence tag or gap marker)
  - step tables carry the schema's core columns (purpose, type, input, output,
    failure, retry, timeout, effect); human and external-wait steps need a
    timeout / expiry path
  - hard-coded secrets
  - agent specification completeness and justification
  - high-risk actions without any human-approval / idempotency discussion
  - leftover placeholders (TBD, TODO, FIXME, {{...}})

Usage:
    python3 validate_workflow.py architecture.md [--depth full] [--strict]
    python3 validate_workflow.py 03-workflow.md --upstream 01-requirements.md 02-architecture.md

    --depth     quick | standard | full. Default: read from a `Depth: ...` line near the
                top of the document, else standard.
    --upstream  earlier documents of the chain; cited upstream IDs (FR-, NFR-, AD-,
                ADR-, INT-, COMP-, A-, Q- ...) are verified against them. If omitted,
                the files named in the document's `Chain:` header are used when they
                sit next to it.
    --strict    treat warnings as errors

Exit code 1 if any error (or any warning with --strict). Standard library only.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_ids as vids  # noqa: E402

# key -> (human name, heading regex)
SECTIONS = {
    "objective": ("Business Objective", r"business objective|objective|business goal"),
    "workflow": ("Workflow Architecture", r"workflow architecture|step definitions?|target process|workflow steps|selected architecture"),
    "errors": ("Error Handling", r"\berrors?\b|failure"),
    "retry": ("Retry & Recovery", r"retry|retries|recover|idempoten"),
    "assumptions": ("Assumptions", r"assumption"),
    "questions": ("Open Questions", r"open question|unknowns?"),
    "requirements": ("Requirements", r"requirement"),
    "trigger": ("Trigger Architecture", r"trigger"),
    "security": ("Security", r"secur"),
    "observability": ("Observability", r"observab|monitoring"),
    "risks": ("Risks", r"\brisks?\b"),
    "blueprint": ("Implementation Blueprint", r"implementation|blueprint|tasks"),
    "actors": ("Actors", r"\bactors?\b|stakeholders"),
    "drivers": ("Workflow Drivers", r"drivers?"),
    "quality": ("Quality Attributes", r"quality attribute"),
    "dataflow": ("Data Flow", r"data flow"),
    "cost": ("Cost", r"\bcost"),
    "scalability": ("Scalability", r"scalab"),
    "alternatives": ("Alternatives", r"alternative|options considered"),
    "selected": ("Selected Architecture", r"selected architecture|chosen architecture|recommended architecture"),
    "diagrams": ("Diagrams", r"diagram"),
    "adrs": ("ADRs", r"\badrs?\b|decision records?|wadr"),
    "testing": ("Testing Strategy", r"test"),
    "validation": ("Validation", r"validation"),
}
QUICK = ["objective", "workflow", "errors", "assumptions", "questions"]
STANDARD = QUICK + ["requirements", "trigger", "security", "observability", "risks", "blueprint"]
FULL = STANDARD + ["retry", "actors", "drivers", "quality", "dataflow", "cost", "scalability",
                   "alternatives", "selected", "diagrams", "adrs", "testing", "validation"]
DEPTHS = {"quick": QUICK, "standard": STANDARD, "full": FULL}

TAG_RE = re.compile(
    r"\[(?:STATED|DOCUMENTED|OBSERVED|INFERRED|ASSUMED|RECOMMENDED|UNKNOWN)\]|"
    r"\b(?:ESTIMATE|ESTIMATED|ASSUMED|ASSUMPTION|UNKNOWN|NOT PROVIDED|REQUIRES VALIDATION)\b|"
    r"\bA-\d{3}\b", re.I)
MONEY_RE = re.compile(r"[$€£]\s?\d|\b\d[\d,.]*\s?(?:USD|EUR|GBP)\b|\bper (?:execution|run|month|1k|1m)\b", re.I)
FIGURE_RES = [
    (re.compile(r"[$€£]\s?\d|\b\d[\d,.]*\s?(?:USD|EUR|GBP)\b", re.I), "money"),
    (re.compile(r"\b\d+(?:\.\d+)?\s?%"), "percentage"),
    (re.compile(r"\b\d[\d,]*\s+(?:applications?|requests?|users?|orders?|tickets?|invoices?|messages?|emails?|documents?|records?|transactions?|candidates?|customers?)\b"
                r"(?:\s+(?:per|a|each|/)\s+(?:second|minute|hour|day|week|month|year))?", re.I), "volume"),
]
SECRET_RES = [
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"), "API key (sk-...)"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key id"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"), "GitHub token"),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key block"),
    (re.compile(r"\bBearer\s+eyJ[A-Za-z0-9_-]{10,}"), "bearer JWT"),
    (re.compile(r"(?i)\b(?:password|passwd|secret|api[_-]?key|token)\s*[:=]\s*['\"]?[A-Za-z0-9/+_\-]{12,}['\"]?"), "credential assignment"),
]
PLACEHOLDER_RE = re.compile(r"\bTBD\b|\bTODO\b|\bFIXME\b|\{\{[^}]*\}\}|lorem ipsum", re.I)
RISKY_RE = re.compile(
    r"\b(?:payments?|refunds?|wire transfers?|delet(?:e|es|ed|ion)|production deploy\w*|credential changes?|"
    r"contracts? signing|legal)\b|\bsend(?:s|ing)?\s+(?:an?\s+)?(?:external\s+)?(?:email|e-mail|message|sms)s?\b", re.I)
SIDE_EFFECT_RE = re.compile(r"\b(?:payments?|refunds?|orders?|send(?:s|ing)?\s+(?:an?\s+)?(?:email|e-mail|message|sms)s?|emails?\s+(?:is\s+)?sent|create[sd]?\s+(?:a\s+)?record)\b", re.I)
HUMAN_RE = re.compile(r"human[- ]in[- ]the[- ]loop|human (?:approval|review)|manual (?:approval|review)|approval gate|\bapprov(?:e|al)\b|reviewer", re.I)
EXTERNAL_TYPE_RE = re.compile(r"api|ai|llm|model|agent|tool|database|http|webhook|notif|email|message|queue|search|retriev|storage", re.I)
HUMAN_TYPE_RE = re.compile(r"human|approval|review", re.I)
WAIT_TYPE_RE = re.compile(r"\bwait|await|reply|callback|external response|confirmation", re.I)
EMPTY_CELL_RE = re.compile(r"^\s*(?:|-|—|–|tbd|\?)\s*$", re.I)
NA_ONLY_RE = re.compile(r"^\s*(?:n/?a|not applicable|none|—|-)\s*\.?\s*$", re.I)


# ---------------------------------------------------------------- parsing

def parse_headings(lines):
    """Return list of dicts: level, title, start (0-based line idx of heading), end (exclusive)."""
    heads, in_fence = [], False
    for idx, line in enumerate(lines):
        st = line.strip()
        if st.startswith("```") or st.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = vids.HEADING_RE.match(st)
        if m:
            heads.append({"level": len(m.group(1)), "title": m.group(2), "start": idx})
    for n, h in enumerate(heads):
        end = len(lines)
        for nxt in heads[n + 1:]:
            if nxt["level"] <= h["level"]:
                end = nxt["start"]
                break
        h["end"] = end
    return heads


def section_body(lines, h):
    """Text of a section excluding its heading line but including subsections."""
    return "\n".join(lines[h["start"] + 1:h["end"]])


def parse_tables(lines):
    """Yield (header_cells, [(line_no, cells)...]) for each Markdown table (1-based line numbers)."""
    tables, i, in_fence = [], 0, False
    while i < len(lines):
        st = lines[i].strip()
        if st.startswith("```") or st.startswith("~~~"):
            in_fence = not in_fence
        if not in_fence and st.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1].strip().lstrip("|")):
            header = split_row(st)
            rows, j = [], i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append((j + 1, split_row(lines[j].strip())))
                j += 1
            tables.append((header, rows))
            i = j
            continue
        i += 1
    return tables


def split_row(row):
    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", row)]


def strip_fences(text):
    out, in_fence = [], False
    for line in text.splitlines():
        st = line.strip()
        if st.startswith("```") or st.startswith("~~~"):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return "\n".join(out)


# ---------------------------------------------------------------- checks

def check_sections(lines, heads, depth, errors, warnings):
    for key in DEPTHS[depth]:
        name, rx = SECTIONS[key]
        matches = [h for h in heads if re.search(rx, h["title"], re.I)]
        if not matches:
            errors.append(f"missing section '{name}' required at depth '{depth}' (add it, or add the heading with 'Not applicable: <reason>')")
            continue
        if not any(len(section_body(lines, h).strip()) > 15 or re.search(r"not applicable|n/a", section_body(lines, h), re.I) for h in matches):
            errors.append(f"section '{matches[0]['title']}' (line {matches[0]['start'] + 1}) is empty")
            continue
        bodies = [section_body(lines, h).strip() for h in matches]
        if all(NA_ONLY_RE.match(b) for b in bodies if b):
            warnings.append(f"section '{matches[0]['title']}' is marked not applicable without a reason")


def check_steps(lines, heads, scan_res, warnings, depth="standard"):
    step_ids = set(i for i in scan_res.defs if i.startswith("STEP-"))
    if not step_ids:
        warnings.append("no STEP-### steps are defined; step failure/retry/timeout coverage cannot be checked")
        return
    covered_in_tables = set()
    for header, rows in parse_tables(lines):
        low = [c.lower() for c in header]
        idrows = [(no, cells) for no, cells in rows if cells and re.match(r"^(?:\*\*|`)?STEP-\d{3}", cells[0])]
        if not idrows:
            continue
        def col(word):
            for k, c in enumerate(low):
                if word in c:
                    return k
            return None
        fcol, rcol, tcol, ycol = col("fail"), col("retry"), col("timeout"), col("type")
        core = [("Name or purpose", col("name") if col("name") is not None else col("purpose")),
                ("Type", ycol), ("Failure", fcol), ("Retry", rcol), ("Timeout", tcol)]
        if depth == "full":   # the detail columns the schema lists; compact tables are fine below full depth
            core += [("Input", col("input")), ("Output", col("output")),
                     ("Effect (read-only / reversible / irreversible)", col("effect") if col("effect") is not None else col("side"))]
        missing = [n for n, c in core if c is None]
        if missing:
            warnings.append(f"step table at line {idrows[0][0]} has no column for: {', '.join(missing)} "
                            f"(security and observability may be stated once in their own sections)")
        for no, cells in idrows:
            sid = re.match(r"^(?:\*\*|`)?(STEP-\d{3})", cells[0]).group(1)
            covered_in_tables.add(sid)
            stype = cells[ycol] if ycol is not None and ycol < len(cells) else ""
            external = bool(EXTERNAL_TYPE_RE.search(stype))
            human = bool(HUMAN_TYPE_RE.search(stype))
            waits = bool(WAIT_TYPE_RE.search(stype))
            for label, c in (("Failure", fcol), ("Retry", rcol), ("Timeout", tcol)):
                if c is None:
                    continue
                val = cells[c] if c < len(cells) else ""
                if EMPTY_CELL_RE.match(val):
                    warnings.append(f"{sid} (line {no}): {label} is empty")
                elif label == "Timeout" and (human or waits) and NA_ONLY_RE.match(val):
                    what = "a human decision" if human else "an external reply"
                    warnings.append(f"{sid} (line {no}): Timeout is 'N/A' but the step waits for {what}; "
                                    f"define the wait limit (or say it is NOT PROVIDED) and the reminder/expiry path")
                elif external and not human and label in ("Retry", "Timeout") and NA_ONLY_RE.match(val):
                    warnings.append(f"{sid} (line {no}): {label} is 'N/A' but the step type looks external; state a policy or a reason")
    for h in heads:
        m = re.match(r"^(?:\*\*|`)?(STEP-\d{3})", h["title"])
        if not m or m.group(1) in covered_in_tables:
            continue
        body = section_body(lines, h).lower()
        miss = [w for w in ("failure", "retry", "timeout") if w not in body]
        if miss:
            warnings.append(f"{m.group(1)} (line {h['start'] + 1}): section does not mention {', '.join(miss)}")
    for sid in sorted(step_ids - covered_in_tables - {m.group(1) for h in heads for m in [re.match(r"^(?:\*\*|`)?(STEP-\d{3})", h["title"])] if m}):
        warnings.append(f"{sid} is defined outside a step table or step heading; cannot verify failure/retry/timeout")


def build_graph(scan_res):
    graph = {}
    for ids in scan_res.line_ids.values():
        for a in ids:
            for b in ids:
                if a != b:
                    graph.setdefault(a, set()).add(b)
    return graph


def reaches(graph, start, prefixes, max_hops):
    seen, frontier = {start}, {start}
    for _ in range(max_hops):
        nxt = set()
        for n in frontier:
            for m in graph.get(n, ()):
                if m not in seen:
                    seen.add(m)
                    nxt.add(m)
        if any(x.split("-")[0] in prefixes for x in nxt):
            return True
        frontier = nxt
    return False


def check_traceability(scan_res, depth, warnings):
    graph = build_graph(scan_res)
    for i in sorted(scan_res.defs):
        p = i.split("-")[0]
        if p == "WR" and not reaches(graph, i, {"STEP", "TASK", "DEC", "TOOL"}, 1):
            warnings.append(f"{i} is not linked to any step, decision, tool or task")
        if depth == "full":
            if p == "WR" and not reaches(graph, i, {"TEST"}, 3):
                warnings.append(f"{i} has no test within reach (WR → … → TEST)")
            if p == "TASK" and not reaches(graph, i, {"TEST"}, 1):
                warnings.append(f"{i} is not linked to any test")


def check_cost_labels(lines, heads, warnings):
    for h in heads:
        if re.search(r"\bcost|pricing|budget", h["title"], re.I):
            for off, line in enumerate(lines[h["start"] + 1:h["end"]]):
                if MONEY_RE.search(line) and not TAG_RE.search(line):
                    warnings.append(f"line {h['start'] + off + 2}: cost figure without an evidence tag or gap marker (e.g. [ASSUMED], REQUIRES VALIDATION)")


def check_figures(text, warnings):
    """Money, percentages and volumes anywhere in the document need an evidence tag or gap marker."""
    in_fence = False
    for no, line in enumerate(text.splitlines(), 1):
        st = line.strip()
        if st.startswith("```") or st.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence or st.startswith("#") or TAG_RE.search(line) or "<!-- ok" in line:
            continue
        for rx, kind in FIGURE_RES:
            m = rx.search(line)
            if m:
                warnings.append(f"line {no}: {kind} figure '{m.group(0).strip()}' without an evidence tag or gap marker "
                                f"(e.g. [ASSUMED], [RECOMMENDED], NOT PROVIDED, REQUIRES VALIDATION)")
                break


def check_secrets(text, errors):
    for no, line in enumerate(text.splitlines(), 1):
        for rx, label in SECRET_RES:
            m = rx.search(line)
            if m:
                errors.append(f"line {no}: possible hard-coded secret ({label}); reference a secret store instead")
                break


def check_agents(lines, heads, text, warnings):
    agent_secs = [h for h in heads if re.search(r"\bagents?\b", h["title"], re.I) and re.search(r"architecture|specification|design", h["title"], re.I)]
    live = [h for h in agent_secs if not re.search(r"not applicable|n/a|no agents?", section_body(lines, h)[:200], re.I)]
    for h in live:
        body = section_body(lines, h).lower()
        reqs = {"goal": r"\bgoal\b", "tools": r"\btools?\b", "permissions / least privilege": r"permission|least privilege",
                "stop conditions": r"stop condition|max(?:imum)? iteration|iteration (?:limit|cap)", "failure conditions": r"failure condition|on failure|cannot complete|escalat",
                "justification": r"justif"}
        miss = [k for k, rx in reqs.items() if not re.search(rx, body)]
        if miss:
            warnings.append(f"agent section '{h['title']}' (line {h['start'] + 1}) does not cover: {', '.join(miss)}")
    if re.search(r"multi-?agent|supervisor agent", strip_fences(text), re.I) and not re.search(r"justif", text, re.I):
        warnings.append("multi-agent design mentioned without any justification")


def check_risk_coverage(text, warnings):
    body = strip_fences(text)
    if RISKY_RE.search(body) and not HUMAN_RE.search(body):
        warnings.append("high-risk actions (payments, deletion, external messages, ...) are mentioned but human approval/review is never discussed")
    if SIDE_EFFECT_RE.search(body) and not re.search(r"idempoten|dedup|duplicate", body, re.I):
        warnings.append("duplicate-sensitive side effects (orders, payments, messages, records) are mentioned but idempotency/duplicate handling is not")


def check_placeholders(text, warnings):
    for no, line in enumerate(text.splitlines(), 1):
        if PLACEHOLDER_RE.search(line):
            warnings.append(f"line {no}: placeholder left in document ({PLACEHOLDER_RE.search(line).group(0)})")


# ---------------------------------------------------------------- entry points

def detect_depth(text, default="standard"):
    """Read `Depth: quick|standard|full` (or `[full]`) from the first lines of a document."""
    for line in text.splitlines()[:40]:
        m = re.search(r"\bdepth\b\W{0,6}(quick|standard|full)\b", line, re.I)
        if m:
            return m.group(1).lower()
    return default


def validate(text, depth="standard", skip_ids=False, upstream=None, chained=False):
    """Return (errors, warnings) for the document text. `upstream` is {id: filename} (see idscan.load_upstream)."""
    lines = text.splitlines()
    heads = parse_headings(lines)
    scan_res = vids.scan(text)
    errors, warnings = [], []
    if not skip_ids:
        if upstream is not None or chained:
            e, w = vids.idscan.check_doc(vids.idscan.scan(text), 3, upstream, True, False, chained=chained)
            errors.extend(e)
            warnings.extend(w)
        else:
            e, _ = vids.check(scan_res)
            errors.extend(e)
    check_sections(lines, heads, depth, errors, warnings)
    check_steps(lines, heads, scan_res, warnings, depth)
    check_traceability(scan_res, depth, warnings)
    check_cost_labels(lines, heads, warnings)
    check_figures(text, warnings)
    check_secrets(text, errors)
    check_agents(lines, heads, text, warnings)
    check_risk_coverage(text, warnings)
    check_placeholders(text, warnings)
    return errors, warnings


def main(argv):
    strict = "--strict" in argv
    depth, upstream_paths, args, mode = None, [], [], "docs"
    it = iter(argv)
    for a in it:
        if a == "--depth":
            depth = next(it, "")
        elif a.startswith("--depth="):
            depth = a.split("=", 1)[1]
        elif a == "--upstream":
            mode = "up"
        elif a.startswith("--"):
            mode = "docs"
        elif mode == "up":
            upstream_paths.append(a)
        else:
            args.append(a)
    if not args or (depth is not None and depth not in DEPTHS):
        print(__doc__)
        return 2
    if upstream_paths:
        missing = [p for p in upstream_paths if not Path(p).exists()]
        if missing:
            print(f"ERROR: upstream file(s) not found: {', '.join(missing)}")
            return 1
    failed = False
    for p in args:
        path = Path(p)
        if not path.exists():
            print(f"ERROR: {p}: file not found")
            failed = True
            continue
        text = path.read_text(encoding="utf-8")
        d = depth or detect_depth(text)
        upstream, chained, note = vids.idscan.auto_upstream(path, text, upstream_paths)
        if note:
            print(f"NOTE: {p}: {note}")
        errors, warnings = validate(text, d, upstream=upstream, chained=chained)
        for w in warnings:
            print(f"WARNING: {p}: {w}")
        for e in errors:
            print(f"ERROR: {p}: {e}")
        print(f"{p} [{d}{'' if depth else ', from document'}]: {len(errors)} error(s), {len(warnings)} warning(s)")
        if errors or (strict and warnings):
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
