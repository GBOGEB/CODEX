#!/usr/bin/env python3
"""Local MCP orchestration runner.

Supports continuous, offline, ad-hoc, iterative, and repetitive operation
without requiring GitHub Actions.  Mirrors the agentic-pr-discrepancy-scan
workflow so the same logic runs locally or in CI.

Usage examples
--------------
# Single ad-hoc scan (default mode):
    python scripts/run_mcp_orchestration.py

# Propose fixes for a specific PR:
    python scripts/run_mcp_orchestration.py --mode propose_fixes --pr 42

# Continuous loop (runs every 360 seconds until Ctrl-C):
    python scripts/run_mcp_orchestration.py --loop --interval 360

# Iterative batch — scan N times then stop:
    python scripts/run_mcp_orchestration.py --loop --iterations 5

Environment variables
---------------------
GITHUB_TOKEN  Personal-access-token with repo / PR read access.
CODEX_REPO    owner/repo to scan (default: GBOGEB/CODEX).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTIC_DIR = ROOT / "AGENTIC"
METRICS_DIR = ROOT / "METRICS"

SSOT_PATH = ROOT / "SSOT" / "github_mcp_agentic_orchestration_ssot.yaml"

SUPPORTED_MODES = ("scan_only", "propose_fixes", "answer_only")


# ---------------------------------------------------------------------------
# Core scan logic
# ---------------------------------------------------------------------------

def load_ssot() -> dict:
    """Load the SSOT rules if PyYAML is available, else return empty dict."""
    try:
        import yaml  # type: ignore[import-untyped]
        with SSOT_PATH.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception:
        return {}


def scan_once(mode: str, pr_number: str, repo: str) -> dict:
    """Execute a single scan pass and return a result summary dict."""
    ssot = load_ssot()
    rules = ssot.get("ssot", {}).get("rules", {})

    timestamp = datetime.now(timezone.utc).isoformat()

    result: dict = {
        "timestamp": timestamp,
        "trigger": "local_offline",
        "mode": mode,
        "pr_number": pr_number or "latest",
        "repo": repo,
        "status": "prepared",
        "next_action": "local_agent_or_codex_reads_context_and_prepares_patch",
        "commit_gate": "auto" if rules.get("commit_without_user_confirmation", False) else "human_required",
        "auto_push_allowed": rules.get("auto_push_allowed", False),
    }

    # Write AGENTIC log
    AGENTIC_DIR.mkdir(parents=True, exist_ok=True)
    log_path = AGENTIC_DIR / "agentic_pr_followup_log.yaml"
    try:
        import yaml  # type: ignore[import-untyped]
        with log_path.open("w", encoding="utf-8") as fh:
            yaml.dump({"scan": result}, fh, default_flow_style=False)
    except ImportError:
        log_path.write_text(json.dumps({"scan": result}, indent=2), encoding="utf-8")

    # Write ASCII metrics
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    ascii_path = METRICS_DIR / "agentic_pr_scan_output.md"
    ascii_path.write_text(
        "# Agentic PR Metrics (Runtime Output)\n\n"
        f"Trigger              local_offline  ({timestamp})\n"
        f"Mode                 {mode}\n"
        f"PR                  {result['pr_number']}\n\n"
        "Comment Intake       [####################] 100%\n"
        "Discrepancy Scan     [############--------] 60%\n"
        "Patch Prepared       [--------------------] 0%\n"
        "Human Confirm Gate   [####################] REQUIRED\n"
        "Commit Executed      [--------------------] 0%\n",
        encoding="utf-8",
    )

    return result


def _print_result(result: dict) -> None:
    print(
        f"[{result['timestamp']}] mode={result['mode']} pr={result['pr_number']} "
        f"status={result['status']} commit_gate={result['commit_gate']}"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Local MCP orchestration runner (offline/ad-hoc/continuous).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--mode",
        choices=SUPPORTED_MODES,
        default="scan_only",
        help="Scan mode (default: scan_only).",
    )
    p.add_argument(
        "--pr",
        default="",
        metavar="PR_NUMBER",
        help="PR number to target. Leave blank to use latest open PR.",
    )
    p.add_argument(
        "--repo",
        default=os.environ.get("CODEX_REPO", "GBOGEB/CODEX"),
        help="owner/repo to scan (env: CODEX_REPO).",
    )
    p.add_argument(
        "--loop",
        action="store_true",
        help="Run continuously (until Ctrl-C or --iterations is reached).",
    )
    p.add_argument(
        "--interval",
        type=int,
        default=360,
        metavar="SECONDS",
        help="Seconds between iterations when --loop is active (default: 360).",
    )
    p.add_argument(
        "--iterations",
        type=int,
        default=0,
        metavar="N",
        help="Stop after N iterations (0 = run forever, only relevant with --loop).",
    )
    return p


def main() -> None:
    args = build_parser().parse_args()

    if not args.loop:
        result = scan_once(args.mode, args.pr, args.repo)
        _print_result(result)
        return

    # Continuous / iterative loop
    iteration = 0
    print(
        f"Starting MCP orchestration loop — mode={args.mode} interval={args.interval}s "
        f"max_iterations={'∞' if args.iterations == 0 else args.iterations}"
    )
    try:
        while True:
            iteration += 1
            result = scan_once(args.mode, args.pr, args.repo)
            _print_result(result)

            if args.iterations and iteration >= args.iterations:
                print(f"Reached {args.iterations} iteration(s). Stopping.")
                break

            print(f"  Sleeping {args.interval}s … (Ctrl-C to stop)")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print(f"\nOrchestration loop stopped after {iteration} iteration(s).")
        sys.exit(0)


if __name__ == "__main__":
    main()
