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
