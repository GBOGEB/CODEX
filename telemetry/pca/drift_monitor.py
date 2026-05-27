#!/usr/bin/env python3
"""
[TOPIC]:       TELEMETRY.PCA
[TRACE]:       TELEMETRY.PCA.DRIFT_MONITOR
[STATE]:       ACTIVE
[WAVE]:        W000
[RENDER]:      PASSED
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

VERSION = "0.1.0"
TRACKED_DIMENSIONS = (
    "structure",
    "renderability",
    "federation",
    "semantic_traceability",
    "orchestration_readiness",
    "drift_stability",
)


def _normalize_metrics(metrics: Mapping[str, Any], label: str) -> dict[str, float]:
    missing = [metric for metric in TRACKED_DIMENSIONS if metric not in metrics]
    if missing:
        missing_list = ", ".join(missing)
        raise ValueError(f"{label} is missing required dimensions: {missing_list}")

    return {metric: float(metrics[metric]) for metric in TRACKED_DIMENSIONS}


def _load_metrics(path: str) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Metrics file must contain a JSON object: {path}")
    return payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bootstrap completion-vector drift monitor.")
    parser.add_argument("--current-file", help="Path to the current completion-vector JSON file.")
    parser.add_argument("--baseline-file", help="Path to the baseline completion-vector JSON file.")
    return parser


def calculate_drift_variance(
    current_metrics: Mapping[str, Any], baseline_metrics: Mapping[str, Any]
) -> float:
    """
    Calculates drift divergence between the current session parameters and established baseline.
    """
    current = _normalize_metrics(current_metrics, "current_metrics")
    baseline = _normalize_metrics(baseline_metrics, "baseline_metrics")

    variance_sum = 0.0

    for metric in TRACKED_DIMENSIONS:
        variance_sum += abs(current[metric] - baseline[metric])

    return variance_sum / len(TRACKED_DIMENSIONS)


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if (args.current_file is None) != (args.baseline_file is None):
        missing_flag = "--current-file" if args.current_file is None else "--baseline-file"
        raise ValueError(
            f"{missing_flag} is missing; provide both --current-file and --baseline-file together or omit both."
        )

    payload: dict[str, Any] = {
        "status": "initialized",
        "topic": "TELEMETRY.PCA",
        "trace": "TELEMETRY.PCA.DRIFT_MONITOR",
        "wave": "W000",
        "version": VERSION,
        "tracked_dimensions": list(TRACKED_DIMENSIONS),
    }

    if args.current_file and args.baseline_file:
        payload.update(
            {
                "status": "evaluated",
                "current_file": args.current_file,
                "baseline_file": args.baseline_file,
                "drift_variance": calculate_drift_variance(
                    _load_metrics(args.current_file),
                    _load_metrics(args.baseline_file),
                ),
            }
        )

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
