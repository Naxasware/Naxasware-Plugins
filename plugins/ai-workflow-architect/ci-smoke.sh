#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S="$HERE/skills/ai-workflow-architect"
for f in "$S"/examples/*.md; do
  [ "$(basename "$f")" = "drift-review.md" ] && continue
  python3 "$S/scripts/validate_workflow.py" "$f" >/dev/null
  python3 "$S/scripts/validate_ids.py" "$f" >/dev/null
  python3 "$S/scripts/validate_diagrams.py" "$f" >/dev/null
done
python3 "$S/scripts/validate_evidence.py" "$S/examples/drift-review.md"
echo "ai-workflow-architect: smoke checks passed."
