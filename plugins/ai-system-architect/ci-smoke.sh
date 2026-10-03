#!/usr/bin/env bash
# CI smoke test for the ai-system-architect plugin.
# Run from anywhere; resolves paths relative to this file.
# Exits non-zero on the first failure (set -e), which CI treats as a failed check.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS="$HERE/skills/ai-system-architect/scripts"
EXAMPLES="$HERE/examples"

echo "== validate_architecture.py against sample-architecture.json =="
python3 "$SCRIPTS/validate_architecture.py" "$EXAMPLES/sample-architecture.json"

echo
echo "== validate_diagrams.py against sample-architecture.json + sample-diagram.mmd =="
python3 "$SCRIPTS/validate_diagrams.py" "$EXAMPLES/sample-architecture.json" "$EXAMPLES/sample-diagram.mmd"

echo
echo "== generate_report.py against sample-architecture.json =="
python3 "$SCRIPTS/generate_report.py" "$EXAMPLES/sample-architecture.json" > /dev/null

echo
echo "== package_skill.py dry run (packages to a temp dir) =="
TMP_OUT="$(mktemp -d)"
python3 "$HERE/tools/package_skill.py" "$HERE/skills/ai-system-architect" "$TMP_OUT"
test -f "$TMP_OUT/ai-system-architect.skill"
rm -rf "$TMP_OUT"

echo
echo "== build_context_bundle.py dry run =="
TMP_MD="$(mktemp -d)/bundle.md"
python3 "$HERE/tools/build_context_bundle.py" -o "$TMP_MD"
test -s "$TMP_MD"
rm -f "$TMP_MD"

echo
echo "ai-system-architect: all smoke checks passed."
