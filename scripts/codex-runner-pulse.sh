#!/usr/bin/env bash
set -euo pipefail

# Generic bounded CODEX ephemeral-runner multiplier.
# Discovery/validation jobs may scale geometrically; authority-bearing mutation
# remains outside this launcher and must be reconciled through the canonical SSOT.
COUNT="${1:-8}"
PULSE_MINUTES="${PULSE_MINUTES:-15}"
ROOT="${RUNNER_ROOT:-$PWD/runners}"
TOKEN="${REGISTRATION_TOKEN:-}"
LABEL="${RUNNER_LABEL:-codex-pulse}"
NAME_PREFIX="${RUNNER_NAME_PREFIX:-codex-pulse}"

case "$COUNT" in 1|2|4|8|16|32|64) ;; *) echo "ERROR: worker count must be a power of two in 1,2,4,8,16,32,64" >&2; exit 2;; esac
[[ "$PULSE_MINUTES" =~ ^[0-9]+$ ]] || { echo "ERROR: PULSE_MINUTES must be an integer" >&2; exit 2; }
[[ -n "$TOKEN" ]] || { echo "ERROR: REGISTRATION_TOKEN is required" >&2; exit 2; }
[[ "$LABEL" =~ ^[A-Za-z0-9._-]+$ ]] || { echo "ERROR: RUNNER_LABEL must be a simple GitHub runner label" >&2; exit 2; }

pids=()
for i in $(seq 1 "$COUNT"); do
  dir="$ROOT/runner-$i"
  [[ -x "$dir/config.sh" && -x "$dir/run.sh" ]] || { echo "ERROR: missing runner distribution in $dir" >&2; exit 2; }
  (
    export RUNNER_DIR="$dir"
    export RUNNER_NAME="${NAME_PREFIX}-$(hostname)-$i-$$"
    export RUNNER_LABELS="$LABEL"
    export REGISTRATION_TOKEN="$TOKEN"
    exec "$(dirname "$0")/w04-register-ephemeral-runner.sh"
  ) &
  pids+=("$!")
done

echo "CODEX_PULSE_STARTED workers=$COUNT label=$LABEL observation_minutes=$PULSE_MINUTES"
echo "Authority mutation is intentionally not performed by this launcher."
sleep "$((PULSE_MINUTES * 60))"
for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || true; done
wait || true
