from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_MATRIX = [
    {"wave": "A66", "bridge": 88, "sync": 91, "pages": 82, "covariance": 60, "abacus": 52},
    {"wave": "A67", "bridge": 89, "sync": 92, "pages": 86, "covariance": 68, "abacus": 64},
    {"wave": "A68", "bridge": 91, "sync": 93, "pages": 91, "covariance": 72, "abacus": 70},
]

DMAIC_PHASES = {
    "bridge": "Control",
    "sync": "Control",
    "pages": "Improve",
    "covariance": "Analyze",
    "abacus": "Improve",
}


def mean(values):
    return sum(values) / len(values) if values else 0.0


def variance(values):
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return sum((v - m) ** 2 for v in values) / (len(values) - 1)


def covariance(xs, ys):
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    mx = mean(xs)
    my = mean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (len(xs) - 1)


def normalize_vector(vector):
    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0:
        return [0.0 for _ in vector]
    return [v / norm for v in vector]


def power_iteration(matrix, rounds=50):
    size = len(matrix)
    vector = [1.0 / math.sqrt(size) for _ in range(size)]
    for _ in range(rounds):
        next_vector = [sum(matrix[i][j] * vector[j] for j in range(size)) for i in range(size)]
        vector = normalize_vector(next_vector)
    eigenvalue = sum(
        vector[i] * sum(matrix[i][j] * vector[j] for j in range(size))
        for i in range(size)
    )
    return eigenvalue, vector


def load_matrix(path):
    if path is None:
        return DEFAULT_MATRIX
    return json.loads(Path(path).read_text(encoding="utf-8"))


def compute_report(rows):
    metrics = [key for key in rows[0].keys() if key != "wave"]
    columns = {metric: [float(row[metric]) for row in rows] for metric in metrics}

    stats = {
        metric: {
            "mean": round(mean(values), 4),
            "variance": round(variance(values), 4),
            "min": min(values),
            "max": max(values),
            "latest": values[-1],
            "delta": round(values[-1] - values[0], 4),
            "dmaic": DMAIC_PHASES.get(metric, "Measure"),
        }
        for metric, values in columns.items()
    }

    cov = []
    for a in metrics:
        row = []
        for b in metrics:
            row.append(round(covariance(columns[a], columns[b]), 6))
        cov.append(row)

    eigenvalue, eigenvector = power_iteration(cov)
    total_variance = sum(cov[i][i] for i in range(len(cov))) or 1.0
    explained = max(0.0, min(eigenvalue / total_variance, 1.0))

    pca = {
        "component": "PC1",
        "explained_variance_ratio": round(explained, 6),
        "eigenvalue": round(eigenvalue, 6),
        "loadings": {
            metric: round(eigenvector[index], 6)
            for index, metric in enumerate(metrics)
        },
    }

    kpi = {
        "average_latest": round(mean([stats[m]["latest"] for m in metrics]), 2),
        "average_delta": round(mean([stats[m]["delta"] for m in metrics]), 2),
        "weakest_metric": min(metrics, key=lambda m: stats[m]["latest"]),
        "strongest_metric": max(metrics, key=lambda m: stats[m]["latest"]),
    }

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "statistics-pca-runtime-complete",
        "waves": [row["wave"] for row in rows],
        "metrics": metrics,
        "statistics": stats,
        "covariance_matrix": {"labels": metrics, "matrix": cov},
        "pca": pca,
        "kpi_summary": kpi,
    }


def main():
    parser = argparse.ArgumentParser(description="Compute runtime statistics, KPI, DMAIC and PCA")
    parser.add_argument("--input")
    parser.add_argument("--out", default="docs/wave_packages/runtime/out/statistics_pca_report.json")
    args = parser.parse_args()

    report = compute_report(load_matrix(args.input))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
