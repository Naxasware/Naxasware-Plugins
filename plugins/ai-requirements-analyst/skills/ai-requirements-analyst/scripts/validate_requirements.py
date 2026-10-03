#!/usr/bin/env python3
"""
Validate an evidence-backed requirements document (markdown) produced by the
AI Requirements Analyst V2 skill.

This checks the V2-specific discipline from references/evidence-model.md:
every requirement block that claims to be tool-derived should carry a
source, an evidence type, and a confidence level — a requirement that
implies verification without actually showing its evidence undermines the
whole point of the evidence model.

Checks:
  - Every requirement ID (FR/NFR/BR/DR/IR/AIR/AR) block that contains an
    "Evidence:" line also has an "Evidence type:" and "Confidence:" line
  - Every "Evidence type:" value is one of the eight recognized types
  - Every "Confidence:" value is High / Medium / Low
  - Blocks that mention CODE_OBSERVED / DATABASE_OBSERVED / API_OBSERVED /
    PROJECT_TRACKER_OBSERVED / DOCUMENTED but have an empty or missing
    "Evidence:" source are flagged — a claimed observation needs a source
  - Requirement blocks with no evidence fields at all are reported as
    informational (they may be legitimately USER_STATED/ASSUMED/INFERRED
    from pure conversation — that's fine, this is not an error)

Usage:
    python validate_requirements.py <path-to-document>

Exit code is 0 if no errors (warnings/info are fine), 1 if errors found.
"""

import re
import sys

REQ_ID_PATTERN = re.compile(r"^\s*(?:#{1,6}\s*)?\**\s*((?:FR|NFR|BR|DR|IR|AIR|AR)-\d{3,4}(?:-\d+)?)\b")

EVIDENCE_TYPES = {
    "USER_STATED", "DOCUMENTED", "CODE_OBSERVED", "DATABASE_OBSERVED",
    "API_OBSERVED", "PROJECT_TRACKER_OBSERVED", "INFERRED", "ASSUMED",
}
OBSERVED_TYPES = {
    "DOCUMENTED", "CODE_OBSERVED", "DATABASE_OBSERVED",
    "API_OBSERVED", "PROJECT_TRACKER_OBSERVED",
}
CONFIDENCE_LEVELS = {"HIGH", "MEDIUM", "LOW"}

FIELD_PATTERN = re.compile(r"^\s*\**\s*(Evidence(?:\s+type)?|Confidence)\s*:\s*(.*)$", re.IGNORECASE)


def split_into_blocks(lines):
    """Split the document into (req_id, start_line, block_lines) chunks,
    one per requirement ID heading found. Everything before the first ID
    and anything not under a requirement ID is ignored for this check."""
    blocks = []
    current_id = None
    current_start = None
    current_lines = []

    def flush():
        if current_id is not None:
            blocks.append((current_id, current_start, current_lines[:]))

    for i, line in enumerate(lines, start=1):
        m = REQ_ID_PATTERN.match(line)
        if m:
            flush()
            current_id = m.group(1)
            current_start = i
            current_lines = [line]
        elif current_id is not None:
            current_lines.append(line)
    flush()
    return blocks


def parse_fields(block_lines):
    fields = {}
    for line in block_lines:
        m = FIELD_PATTERN.match(line)
        if m:
            key = m.group(1).strip().lower()
            key = "evidence_type" if key.startswith("evidence type") else key.lower()
            fields.setdefault(key, []).append(m.group(2).strip())
    return fields


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_requirements.py <path-to-document>")
        sys.exit(2)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    blocks = split_into_blocks(lines)

    errors = []
    warnings = []
    info = []
    evidence_backed_count = 0
    plain_count = 0

    for req_id, start_line, block_lines in blocks:
        fields = parse_fields(block_lines)
        has_evidence = "evidence" in fields
        has_type = "evidence_type" in fields
        has_confidence = "confidence" in fields

        if not (has_evidence or has_type or has_confidence):
            plain_count += 1
            continue  # not claiming to be evidence-backed; nothing to check

        evidence_backed_count += 1

        if not has_evidence or not fields["evidence"][0]:
            errors.append(f"{req_id} (line {start_line}): has evidence-type/confidence "
                           f"fields but no 'Evidence:' source listed")
        if not has_type:
            errors.append(f"{req_id} (line {start_line}): has an 'Evidence:' source but "
                           f"no 'Evidence type:' — can't tell how it was derived")
        if not has_confidence:
            errors.append(f"{req_id} (line {start_line}): is evidence-backed but has no "
                           f"'Confidence:' level (High/Medium/Low)")

        if has_type:
            raw_types = re.split(r"[,;]", fields["evidence_type"][0])
            for t in raw_types:
                t_clean = t.strip().upper()
                if not t_clean:
                    continue
                if t_clean not in EVIDENCE_TYPES:
                    warnings.append(f"{req_id} (line {start_line}): unrecognized evidence "
                                     f"type '{t.strip()}' — expected one of {sorted(EVIDENCE_TYPES)}")
                if t_clean in OBSERVED_TYPES and (not has_evidence or not fields["evidence"][0]):
                    errors.append(f"{req_id} (line {start_line}): claims {t_clean} but has "
                                   f"no actual evidence source listed")

        if has_confidence:
            conf_clean = fields["confidence"][0].strip().upper()
            if conf_clean not in CONFIDENCE_LEVELS:
                warnings.append(f"{req_id} (line {start_line}): confidence value "
                                 f"'{fields['confidence'][0]}' is not High/Medium/Low")

    print(f"Checked {path}")
    print(f"Found {len(blocks)} requirement blocks "
          f"({evidence_backed_count} evidence-backed, {plain_count} plain/user-stated).\n")

    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("No errors.")

    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"  - {w}")

    if plain_count and evidence_backed_count:
        info.append(f"{plain_count} requirement(s) have no evidence fields at all — fine if "
                     f"they're genuinely USER_STATED/ASSUMED/INFERRED from pure conversation, "
                     f"but worth a second look if this document is supposed to be tool-verified.")
    if info:
        print("\nINFO:")
        for i in info:
            print(f"  - {i}")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
