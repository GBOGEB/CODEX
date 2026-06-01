"""Emit machine-consumable runtime status JSON for federation consumers."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEPLOY = REPO_ROOT / "docs" / "wave_packages" / "runtime" / "out" / "deployment_readiness.json"
DEFAULT_REALITY = REPO_ROOT / "docs" / "wave_packages" / "runtime" / "out" / "reality_tracker.json"
DEFAULT_OUT = REPO_ROOT / "reports" / "runtime_status.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_runtime_status(deployment: dict, reality: dict) -> dict:
    deployment_score = float(deployment.get("completion_percent", 0))
    reality_score = float(reality.get("average_actual", 0))
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if deployment_score >= 90 and reality_score >= 50 else "failed",
        "release_gate": {
            "deployment_threshold": 90,
            "reality_threshold": 50,
            "deployment_score": deployment_score,
            "reality_score": reality_score,
            "deployment_passed": deployment_score >= 90,
            "reality_passed": reality_score >= 50,
        },
        "source_artifacts": {
            "deployment_readiness": "docs/wave_packages/runtime/out/deployment_readiness.json",
            "reality_tracker": "docs/wave_packages/runtime/out/reality_tracker.json",
        },
        "deployment": deployment,
        "reality": reality,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit reports/runtime_status.json from runtime evidence")
    parser.add_argument("--deployment-json", type=Path, default=DEFAULT_DEPLOY)
    parser.add_argument("--reality-json", type=Path, default=DEFAULT_REALITY)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    deployment = _load_json(args.deployment_json)
    reality = _load_json(args.reality_json)
    payload = build_runtime_status(deployment, reality)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote runtime status report → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
