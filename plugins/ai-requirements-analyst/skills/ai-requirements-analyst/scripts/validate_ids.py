#!/usr/bin/env python3
"""
Validate requirement IDs in a requirements document (markdown or plain text).

Checks:
  - Every ID follows the standard scheme (PREFIX-NNN)
  - No duplicate IDs
  - No gaps that look like accidental skips vs. intentional removals (reported, not failed)
  - Every ID referenced elsewhere in the doc (e.g. in a traceability matrix or
    a requirement's "Dependencies" / "Business rules" field) actually exists

Usage:
    python validate_ids.py <path-to-document>

Exit code is 0 if no errors (warnings are fine), 1 if errors found.
"""

import re
import sys
from collections import defaultdict

VALID_PREFIXES = {
    "BO", "ST", "ACT", "FR", "NFR", "BR", "DR", "IR", "AIR", "AR",
    "UC", "US", "AC", "A", "Q", "CON", "DEP",
}

# Matches PREFIX-NNN or PREFIX-NNN-N (sub-criteria like AC-007-1)
ID_PATTERN = re.compile(r"\b([A-Z]{1,4})-(\d{3,4})(?:-(\d+))?\b")


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def find_all_ids(text):
    """Return list of (full_match, prefix, number, sub, line_no)."""
    results = []
    for i, line in enumerate(text.splitlines(), start=1):
        for m in ID_PATTERN.finditer(line):
            prefix, number, sub = m.group(1), m.group(2), m.group(3)
            results.append((m.group(0), prefix, number, sub, i))
    return results


def find_definitions(text):
    """
    A 'definition' is an ID appearing at the start of a line or heading
    (e.g. '### FR-001' or 'FR-001 — Create Vehicle' or '**FR-001**'),
    as opposed to a reference to it elsewhere.
    """
    defs = defaultdict(list)
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip().lstrip("#").strip().lstrip("*").strip()
        m = ID_PATTERN.match(stripped)
        if m:
            full = m.group(0)
            defs[full].append(i)
    return defs


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_ids.py <path-to-document>")
        sys.exit(2)

    path = sys.argv[1]
    text = load(path)

    all_ids = find_all_ids(text)
    definitions = find_definitions(text)

    errors = []
    warnings = []

    # 1. Check prefixes are valid
    unknown_prefixes = {p for (_, p, _, _, _) in all_ids if p not in VALID_PREFIXES}
    if unknown_prefixes:
        warnings.append(
            f"IDs with prefixes not in the standard scheme (may be false positives, "
            f"e.g. figure/table labels): {sorted(unknown_prefixes)}"
        )

    # 2. Check for duplicate definitions
    for full_id, lines in definitions.items():
        if len(lines) > 1:
            errors.append(f"Duplicate definition of {full_id} on lines {lines}")

    # 3. Check every reference resolves to a definition
    referenced = defaultdict(list)
    for (full, prefix, number, sub, line_no) in all_ids:
        if prefix in VALID_PREFIXES:
            referenced[full].append(line_no)

    undefined = [full for full in referenced if full not in definitions]
    if undefined:
        for full in sorted(undefined):
            errors.append(
                f"{full} is referenced (lines {referenced[full]}) but never defined"
            )

    # 4. Check numeric sequence per prefix for suspicious gaps
    by_prefix = defaultdict(set)
    for full_id in definitions:
        m = ID_PATTERN.match(full_id)
        if m and m.group(1) in VALID_PREFIXES and not m.group(3):
            by_prefix[m.group(1)].add(int(m.group(2)))

    for prefix, numbers in sorted(by_prefix.items()):
        nums = sorted(numbers)
        gaps = [n for n in range(nums[0], nums[-1] + 1) if n not in numbers]
        if gaps:
            warnings.append(
                f"{prefix}: numbering has gaps at {gaps} (fine if intentional "
                f"— e.g. a removed requirement — otherwise check for typos)"
            )

    # Report
    print(f"Checked {path}")
    print(f"Found {sum(len(v) for v in definitions.values())} ID definitions "
          f"across {len(definitions)} unique IDs.\n")

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

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
