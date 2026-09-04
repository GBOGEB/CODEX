#!/usr/bin/env python3
"""Execute the existing CODEX MCP federation sweep from CI or a local checkout.

This runner is intentionally thin: it does not introduce a second orchestrator.
It invokes ``MCPSweepEngine`` and writes hashable telemetry outputs that can be
consumed by governance/Pages jobs.  The sweep is public-repository metadata
only and must not ingest private cryoplant tender/source content.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.federation.mcp_sweep_engine import MCPSweepEngine
from src.github_interface import GitHubInterface


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run CODEX MCP federation sweep")
    parser.add_argument("--owner", default=os.getenv("GITHUB_REPOSITORY_OWNER", "GBOGEB"))
    parser.add_argument(
        "--repo",
        default=(os.getenv("GITHUB_REPOSITORY", "GBOGEB/CODEX").split("/", 1)[-1]),
    )
    parser.add_argument(
        "--session-log-dir",
        type=Path,
        default=ROOT / "outputs" / "sessions",
    )
    parser.add_argument(
        "--lineage-path",
        type=Path,
        default=ROOT / "MANIFEST" / "federation_lineage.yaml",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "outputs" / "federation",
    )
    parser.add_argument(
        "--require-token",
        action="store_true",
        help="Fail before execution when GITHUB_TOKEN is absent.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    token = os.getenv("GITHUB_TOKEN", "")
    if args.require_token and not token:
        raise SystemExit("GITHUB_TOKEN is required for this execution mode")

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    telemetry_path = output_dir / "sweep_telemetry.md"
    rtm_delta_path = output_dir / "rtm_delta.md"
    summary_path = output_dir / "sweep_summary.json"

    github = GitHubInterface()
    engine = MCPSweepEngine(
        repo_path=ROOT,
        github_interface=github,
        github_token=token,
    )
    result = engine.run(
        owner=args.owner,
        repo=args.repo,
        session_log_dir=args.session_log_dir,
        lineage_path=args.lineage_path,
        telemetry_output_path=telemetry_path,
        rtm_delta_output_path=rtm_delta_path,
    )

    summary = {
        "schema_version": "1.0",
        "execution": "MCP_FEDERATION_SWEEP",
        "repository": f"{args.owner}/{args.repo}",
        "public_metadata_only": True,
        "formal_credit_delta": 0,
        **result,
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
