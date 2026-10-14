#!/usr/bin/env python3
"""
Check an architecture document for ID problems in the schemes this skill uses:

    AD-###    architecture driver          COMP-###  component
    ADR-###   architecture decision        INT-###   integration
    RISK-###  architecture risk            EVT-###   event
    DEBT-###  architecture debt item       A-### / Q-###  assumption / open question

and, when the document cites requirement IDs from `ai-requirements-analyst`
(FR-, NFR-, BR-, AIR-, IR-, CON-, DEP-, AC- ...), verifies those too.

How an ID counts as *defined* (same grammar in all three chain skills): it is
the first thing in a heading, list item, table row (first cell), bold line or
plain line, outside code fences, and not under a heading containing
"Traceab", "Coverage", "Cross-ref", "Carried forward" or "Upstream" (those
sections only reference). A line containing `<!-- ref -->` is reference-only.
Ranges such as "A-001 to A-008" reference every ID in the range.

Usage:
    python3 validate_ids.py 02-architecture.md
    python3 validate_ids.py 02-architecture.md --upstream 01-requirements.md

    --upstream   earlier documents of the chain (default: the files named in the document's
                 `Chain:` header, when they sit next to it). A cited FR-/NFR-/... that the
                 requirements never defined is an error (a typo or an invented
                 requirement); redefining an upstream ID here is an error.
                 Without it, such citations only produce one summary warning.
    --orphans    also warn about defined IDs that nothing references

Exit code 1 if any error was found. Standard library only.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import idscan  # noqa: E402

STAGE = 2
ORPHAN_PREFIXES = {"AD", "COMP", "INT", "EVT"}


def main(argv):
    return idscan.cli(argv, STAGE, __doc__, malformed_is_error=False, gaps=True,
                      orphan_prefixes=ORPHAN_PREFIXES)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
