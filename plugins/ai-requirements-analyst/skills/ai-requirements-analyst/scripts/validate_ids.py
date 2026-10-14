#!/usr/bin/env python3
"""
Validate a requirements document (Markdown or plain text).

Checks:
  - IDs follow the scheme PREFIX-NNN (AC- sub-criteria are AC-<FR number>-<n>)
  - no ID is defined twice; every ID that is cited is defined somewhere
  - numbering gaps (reported as warnings; fine if a requirement was removed)
  - TESTABILITY: every functional requirement (FR-) has at least one
    acceptance criterion named AC-<same number>-<n> (AC-007-1 verifies
    FR-007; a matrix row that merely lists both IDs does not count); every AC
    points at an existing FR.

How an ID counts as *defined* (same grammar in all three chain skills): it is
the first thing in a heading, list item, table row (first cell), bold line or
plain line, outside code fences, and not under a heading containing
"Traceab", "Coverage", "Cross-ref", "Carried forward" or "Upstream" (those
sections only reference). A line containing `<!-- ref -->` is reference-only.
Ranges such as "FR-001 to FR-013" reference every ID in the range.

Usage:
    python3 validate_ids.py 01-requirements.md [--strict]

    --strict   treat warnings as errors (includes FRs without acceptance criteria)

Exit code 1 if any error was found. Standard library only.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import idscan  # noqa: E402

STAGE = 1


def testability(s):
    """Warnings for FRs without an acceptance criterion and ACs without an FR."""
    warnings = []
    frs = sorted(i for i in s.defs if i.startswith("FR-") and i.count("-") == 1)
    acs = sorted(i for i in s.defs if i.startswith("AC-"))
    ac_nums = {i.split("-")[1] for i in acs}
    for fr in frs:
        if fr.split("-")[1] not in ac_nums:
            warnings.append(f"{fr} (line {s.defs[fr][0]}) has no acceptance criterion; add AC-{fr.split('-')[1]}-1 "
                            f"(Given/When/Then) or state why it cannot be tested")
    fr_nums = {i.split("-")[1] for i in frs}
    for ac in acs:
        if ac.split("-")[1] not in fr_nums:
            warnings.append(f"{ac} (line {s.defs[ac][0]}) does not match any functional requirement "
                            f"(AC ids are AC-<FR number>-<n>)")
    return warnings


def main(argv):
    strict = "--strict" in argv
    args = [a for a in argv if a != "--strict"]
    if len(args) != 1 or args[0].startswith("--"):
        print(__doc__)
        return 2
    path = Path(args[0])
    if not path.exists():
        print(f"ERROR: {path}: file not found")
        return 1
    s = idscan.scan(path.read_text(encoding="utf-8"))
    errors, warnings = idscan.check_doc(s, STAGE, None, malformed_is_error=False, gaps=True)
    warnings += testability(s)
    for w in warnings:
        print(f"WARNING: {path}: {w}")
    for e in errors:
        print(f"ERROR: {path}: {e}")
    print(f"{path}: {len(s.defs)} ID(s) defined, {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors or (strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
