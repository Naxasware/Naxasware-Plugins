#!/usr/bin/env python3
"""
Check a workflow-architecture document for ID problems.

Finds duplicate definitions, dangling references (an ID used but never
defined) and malformed IDs (fewer than three digits) for: BO WR WD STEP DEC
TOOL TASK TEST WADR WRISK A Q.

How an ID counts as *defined* (same grammar in all three chain skills): it is
the first thing in a heading, list item, table row (first cell), bold line or
plain line, outside code fences, and not under a heading containing
"Traceab", "Coverage", "Cross-ref", "Carried forward" or "Upstream" (those
sections only reference). A line containing `<!-- ref -->` is reference-only.
Ranges such as "A-001 to A-008" reference every ID in the range.

Usage:
    python3 validate_ids.py architecture.md [more.md ...] [--orphans]
    python3 validate_ids.py 03-workflow.md --upstream 01-requirements.md 02-architecture.md

    --orphans    also warn about defined IDs that nothing references
    --upstream   earlier documents of the chain (default: the files named in the document's
                 `Chain:` header, when they sit next to it). IDs they define (FR-, NFR-,
                 AD-, ADR-, INT-, COMP-, A-, Q- ...) resolve as references;
                 a cited upstream-style ID found nowhere is an error; redefining
                 an upstream ID here is an error.

Exit code 1 if any error was found. Standard library only.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import idscan  # noqa: E402

STAGE = 3
# Prefixes this validator tracks when the document is checked on its own
# (the stage's own prefixes, shared A/Q, and BO which standalone documents define).
PREFIXES = idscan.OWNED[3] + idscan.SHARED + ["BO"]
ORPHAN_PREFIXES = {"WR", "WD", "TOOL", "DEC", "TASK", "STEP", "WADR", "WRISK"}
HEADING_RE = idscan.HEADING_RE
Scan = idscan.Scan


def scan(text):
    """Scan with this stage's prefixes (used by validate_workflow, validate_diagrams, generate_report)."""
    return idscan.scan(text, PREFIXES)


def check(s, orphans=False, upstream=None):
    return idscan.check_doc(s, STAGE, upstream, malformed_is_error=True, gaps=False,
                            orphans=orphans, orphan_prefixes=ORPHAN_PREFIXES)


def main(argv):
    return idscan.cli(argv, STAGE, __doc__, malformed_is_error=True, gaps=False,
                      orphan_prefixes=ORPHAN_PREFIXES)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
