"""Emit governance snapshot JSON from check outcomes."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO_ROOT / "reports" / "governance_snapshot.json"


_OUTCOME_ALIASES = {"success": "passed", "failure": "failed"}


def _parse_check(raw: str) -> tuple[str, str]:
    if "=" not in raw:
        raise ValueError(f"Invalid --check value '{raw}', expected name=status")
    name, status = raw.split("=", 1)
    status = status.strip().lower()
    # CI callers pass GitHub Actions' `steps.<id>.outcome` verbatim, which
    # uses success/failure/skipped/cancelled — not this script's own
    # passed/failed vocabulary. Without this normalization every check
    # compared unequal to "passed" and the snapshot silently reported every
    # run as failed regardless of actual CI outcome.
    status = _OUTCOME_ALIASES.get(status, status)
    return name.strip(), status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit reports/governance_snapshot.json")
    parser.add_argument(
        "--check",
        action="append",
        default=[],
        help="Check status as name=status (status should be passed/failed/skipped).",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    checks = []
    for raw in args.check:
        name, status = _parse_check(raw)
        checks.append({"name": name, "status": status, "passed": status == "passed"})

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if checks and all(c["passed"] for c in checks) else "failed",
        "repo": os.environ.get("GITHUB_REPOSITORY", "local"),
        "sha": os.environ.get("GITHUB_SHA", ""),
        "ref": os.environ.get("GITHUB_REF", ""),
        "workflow": os.environ.get("GITHUB_WORKFLOW", ""),
        "checks": checks,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote governance snapshot → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
