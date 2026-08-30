#!/usr/bin/env bash
set -euo pipefail

# Launch N already-unpacked ephemeral runner directories for a bounded experiment.
# Each runner consumes one registration token. For repository registration tokens,
# the same still-valid token may be used to configure multiple runners, subject to
# GitHub permissions/expiry. No token is written to disk by this script.

COUNT="${1:-2}"
PULSE_MINUTES="${PULSE_MINUTES:-15}"
ROOT="${RUNNER_ROOT:-$PWD/runners}"
TOKEN="${REGISTRATION_TOKEN:-}"

case "$COUNT" in 2|4|8) ;; *) echo "ERROR: worker count must be 2, 4, or 8" >&2; exit 2;; esac
[[ "$PULSE_MINUTES" =~ ^[0-9]+$ ]] || { echo "ERROR: PULSE_MINUTES must be an integer" >&2; exit 2; }
[[ -n "$TOKEN" ]] || { echo "ERROR: REGISTRATION_TOKEN is required" >&2; exit 2; }

pids=()
for i in $(seq 1 "$COUNT"); do
  dir="$ROOT/runner-$i"
  [[ -x "$dir/config.sh" && -x "$dir/run.sh" ]] || { echo "ERROR: missing runner distribution in $dir" >&2; exit 2; }
  (
    export RUNNER_DIR="$dir"
    export RUNNER_NAME="codex-w04-$(hostname)-$i-$$"
    export RUNNER_LABELS="codex-w04"
    export REGISTRATION_TOKEN="$TOKEN"
    exec "$(dirname "$0")/w04-register-ephemeral-runner.sh"
  ) &
  pids+=("$!")
done

echo "Started $COUNT ephemeral runners; observation pulse=${PULSE_MINUTES}m"
echo "Dispatch priority work separately after GitHub shows at least one runner online."

# This timeout bounds the observation process; ephemeral runners also deregister
# automatically after processing one job. Remaining listeners are terminated.
sleep "$((PULSE_MINUTES * 60))"
for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || true; done
wait || true
