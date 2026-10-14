#!/usr/bin/env bash
# CI smoke test for the ai-requirements-analyst plugin.
# Run from anywhere; resolves paths relative to this file.
# Exits non-zero on the first failure (set -e), which CI treats as a failed check.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS="$HERE/skills/ai-requirements-analyst/scripts"
EXAMPLES="$HERE/examples"

echo "== validate_ids.py against sample-discovery-report.md =="
python3 "$SCRIPTS/validate_ids.py" "$EXAMPLES/sample-discovery-report.md"

echo
echo "== validate_ids.py against sample-audit-input.md =="
python3 "$SCRIPTS/validate_ids.py" "$EXAMPLES/sample-audit-input.md"

echo
echo "== validate_requirements.py against sample-evidence-comparison.md =="
python3 "$SCRIPTS/validate_requirements.py" "$EXAMPLES/sample-evidence-comparison.md"

echo
echo "== generate_report.py against sample-requirements.json (all formats) =="
python3 "$SCRIPTS/generate_report.py" "$EXAMPLES/sample-requirements.json" --format markdown > /dev/null
python3 "$SCRIPTS/generate_report.py" "$EXAMPLES/sample-requirements.json" --format csv > /dev/null
python3 "$SCRIPTS/generate_report.py" "$EXAMPLES/sample-requirements.json" --format matrix > /dev/null

echo
echo
echo "== chain example: stage 1 document =="
python3 "$SCRIPTS/validate_ids.py" "$EXAMPLES/chain-example/01-requirements.md" --strict
python3 "$SCRIPTS/validate_requirements.py" "$EXAMPLES/chain-example/01-requirements.md"

echo
echo "== regression: arrow-style traceability must not report duplicates =="
TMP_DOC="$(mktemp -d)/arrow.md"
printf '> Chain: stage=1 | skill=ai-requirements-analyst | upstream=none | next=ai-system-architect\n\n## Business Objectives\nBO-001: Reduce manual work.\n\n## Functional Requirements\nFR-001 - Do the thing\nAC-001-1: Given a, when b, then c.\n\n## Traceability\nBO-001 -> FR-001 -> AC-001-1\n' > "$TMP_DOC"
python3 "$SCRIPTS/validate_ids.py" "$TMP_DOC" --strict >/dev/null
rm -f "$TMP_DOC"

echo
echo "== regression: a functional requirement without a criterion must be reported =="
NOAC="$(mktemp -d)/noac.md"
printf '> Chain: stage=1 | skill=ai-requirements-analyst | upstream=none | next=ai-system-architect\n\nBO-001: Reduce manual work.\n\nFR-001 - Do the thing\n' > "$NOAC"
if python3 "$SCRIPTS/validate_ids.py" "$NOAC" --strict >/dev/null; then echo "FAIL: missing acceptance criterion not detected"; exit 1; fi
rm -f "$NOAC"

echo
echo "== chain scripts identical across plugins (drift check) =="
python3 - "$SCRIPTS" "$HERE" <<'PY'
import hashlib, sys
from pathlib import Path
mine_dir, here = Path(sys.argv[1]), Path(sys.argv[2])
bad = []
for name in ("idscan.py", "validate_chain.py"):
    mine = hashlib.sha256((mine_dir / name).read_bytes()).hexdigest()
    for sib in sorted(here.parent.glob(f"ai-*/skills/ai-*/scripts/{name}")):
        if hashlib.sha256(sib.read_bytes()).hexdigest() != mine:
            bad.append(f"{name} differs from {sib}")
if bad:
    print("FAIL: " + "; ".join(bad)); sys.exit(1)
print("chain scripts identical")
PY

echo "== package_skill.py dry run (packages to a temp dir) =="
TMP_OUT="$(mktemp -d)"
python3 "$HERE/tools/package_skill.py" "$HERE/skills/ai-requirements-analyst" "$TMP_OUT"
test -f "$TMP_OUT/ai-requirements-analyst.skill"
rm -rf "$TMP_OUT"

echo
echo "== build_context_bundle.py dry run =="
TMP_MD="$(mktemp -d)/bundle.md"
python3 "$HERE/tools/build_context_bundle.py" -o "$TMP_MD"
test -s "$TMP_MD"
rm -f "$TMP_MD"

echo
echo "ai-requirements-analyst: all smoke checks passed."
