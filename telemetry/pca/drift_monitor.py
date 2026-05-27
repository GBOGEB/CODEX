#!/usr/bin/env python3
"""
[TOPIC]:       TELEMETRY.PCA
[TRACE]:       TELEMETRY.PCA.DRIFT_MONITOR
[STATE]:       ACTIVE
[WAVE]:        W000
[RENDER]:      PASSED
"""

import argparse
import json
from pathlib import Path

TRACKED_DIMENSIONS = [
    "structure",
    "renderability",
    "federation",
    "semantic_traceability",
    "orchestration_readiness",
    "drift_stability",
]


def calculate_drift_variance(current_metrics, baseline_metrics):
    """Calculate average absolute drift across the tracked telemetry dimensions."""
    variance_sum = 0.0

    for metric in TRACKED_DIMENSIONS:
        variance_sum += abs(current_metrics.get(metric, 0.0) - baseline_metrics.get(metric, 0.0))

    return variance_sum / len(TRACKED_DIMENSIONS)


def load_metrics(path):
    """Load a JSON object containing telemetry metrics."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} must contain valid JSON metrics: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object of metrics")
    return data


def build_drift_report(current_metrics, baseline_metrics):
    """Build a simple drift report for CLI output and downstream tooling."""
    deltas = {}
    for metric in TRACKED_DIMENSIONS:
        baseline_value = float(baseline_metrics.get(metric, 0.0))
        current_value = float(current_metrics.get(metric, 0.0))
        deltas[metric] = round(current_value - baseline_value, 6)

    return {
        "tracked_dimensions": TRACKED_DIMENSIONS,
        "drift_variance": round(calculate_drift_variance(current_metrics, baseline_metrics), 6),
        "deltas": deltas,
    }


def parse_args(argv=None):
    """Parse CLI arguments for optional drift comparisons."""
    parser = argparse.ArgumentParser(
        description="Bootstrap PCA drift monitor for Wave W000 telemetry."
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        help="Path to a JSON file containing baseline telemetry metrics.",
    )
    parser.add_argument(
        "--current",
        type=Path,
        help="Path to a JSON file containing current telemetry metrics.",
    )
    args = parser.parse_args(argv)

    if (args.baseline is None) != (args.current is None):
        parser.error("Both --baseline and --current arguments are required when using drift comparison")

    return args


def main(argv=None):
    args = parse_args(argv)

    if not args.baseline:
        print("[TELEMETRY.PCA.DRIFT_MONITOR] System initialized. Tracking operational loops.")
        return 0

    report = build_drift_report(
        load_metrics(args.current),
        load_metrics(args.baseline),
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
