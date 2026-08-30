#!/usr/bin/env bash
set -euo pipefail

REPO="${REPO:-GBOGEB/CODEX}"
REF="${REF:-main}"
WORKFLOW="${WORKFLOW:-qps-w04-keb-receipt.yml}"

command -v gh >/dev/null 2>&1 || { echo "ERROR: GitHub CLI (gh) is required." >&2; exit 2; }
gh auth status >/dev/null

# Dispatch only the governed W04 workflow's opt-in priority lane.
gh workflow run "$WORKFLOW" \
  --repo "$REPO" \
  --ref "$REF" \
  --raw-field priority_runner=true

echo "Dispatched $WORKFLOW on $REF with priority_runner=true"
echo "Recent runs:"
gh run list --repo "$REPO" --workflow "$WORKFLOW" --limit 5
