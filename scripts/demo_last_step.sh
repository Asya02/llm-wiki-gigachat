#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

CORPUS="business-fast-demo"
INGEST_FILE=""

usage() {
  cat <<'EOF'
Usage:
  scripts/demo_last_step.sh [--corpus business-fast-demo] [--ingest-file raw/05_additional_followup_signal.md]

What this script does:
  1) Optionally ingests one raw file (only that file).
  2) Clears only query/lint marks in outputs/<corpus>/.progress.
  3) Re-runs answer generation and lint.

Typical demo command:
  scripts/demo_last_step.sh --ingest-file raw/05_additional_followup_signal.md
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --corpus)
      CORPUS="${2:-}"
      shift 2
      ;;
    --ingest-file)
      INGEST_FILE="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

WORKSPACE="$ROOT_DIR/outputs/$CORPUS"
PROGRESS_FILE="$WORKSPACE/.progress"

if [[ ! -d "$WORKSPACE" ]]; then
  echo "Workspace not found: $WORKSPACE" >&2
  echo "Run base build first:" >&2
  echo "  uv run python -u run_demo.py $CORPUS --build-only" >&2
  exit 1
fi

if [[ -n "$INGEST_FILE" ]]; then
  echo ">>> Ingesting one file: $INGEST_FILE"
  uv run python -u run_demo.py "$CORPUS" --ingest-file "$INGEST_FILE"
fi

if [[ -f "$PROGRESS_FILE" ]]; then
  echo ">>> Clearing query/lint marks in .progress"
  awk '!/^query:/ && $0!="lint"' "$PROGRESS_FILE" > "$PROGRESS_FILE.tmp"
  mv "$PROGRESS_FILE.tmp" "$PROGRESS_FILE"
fi

echo ">>> Rebuilding answers from updated wiki"
uv run python -u run_demo.py "$CORPUS" --answer-only

echo
echo "Done. Open:"
echo "  $WORKSPACE/wiki/incident-summary.md"
echo "  $WORKSPACE/reports/final_incident_summary.md"
