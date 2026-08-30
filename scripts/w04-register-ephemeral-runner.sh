#!/usr/bin/env bash
set -euo pipefail

# Register and start one ephemeral CODEX W04 runner.
# The GitHub Actions runner distribution must already be unpacked in RUNNER_DIR.
# Never commit registration tokens. Obtain a fresh repository registration token
# from GitHub Settings > Actions > Runners > New self-hosted runner, or through
# an appropriately privileged API client. GitHub registration tokens expire.

REPO_URL="${REPO_URL:-https://github.com/GBOGEB/CODEX}"
RUNNER_DIR="${RUNNER_DIR:-$PWD}"
RUNNER_NAME="${RUNNER_NAME:-codex-w04-$(hostname)-$$}"
RUNNER_LABELS="${RUNNER_LABELS:-codex-w04}"
REGISTRATION_TOKEN="${REGISTRATION_TOKEN:-}"

if [[ -z "$REGISTRATION_TOKEN" ]]; then
  echo "ERROR: REGISTRATION_TOKEN is required and must be supplied via environment." >&2
  exit 2
fi

cd "$RUNNER_DIR"
if [[ ! -x ./config.sh || ! -x ./run.sh ]]; then
  echo "ERROR: RUNNER_DIR must contain executable config.sh and run.sh from the GitHub Actions runner distribution." >&2
  exit 2
fi

./config.sh \
  --unattended \
  --url "$REPO_URL" \
  --token "$REGISTRATION_TOKEN" \
  --name "$RUNNER_NAME" \
  --labels "$RUNNER_LABELS" \
  --ephemeral \
  --replace

echo "Starting ephemeral runner: $RUNNER_NAME labels=$RUNNER_LABELS"
exec ./run.sh
