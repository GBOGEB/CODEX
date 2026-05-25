"""Executable covariance runtime.

Provides deterministic covariance validation and health scoring for runtime
federation continuity.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable


def validate_square_matrix(matrix: list[list[float]]) -> int:
    if not matrix or not isinstance(matrix, list):
        raise ValueError("Matrix must be a non-empty list")
    size = len(matrix)
    for row in matrix:
        if len(row) != size:
            raise ValueError("Matrix must be square")
        for value in row:
            if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                raise ValueError("Matrix values must be finite")
    return size


def symmetry_error(matrix: list[list[float]]) -> float:
    size = validate_square_matrix(matrix)
    error = 0.0
    for i in range(size):
        for j in range(size):
            error = max(error, abs(matrix[i][j] - matrix[j][i]))
    return round(error, 8)


def covariance_health(matrix: list[list[float]]) -> dict:
    # Validate matrix first to ensure it's square and finite
    size = validate_square_matrix(matrix)
    sym_error = symmetry_error(matrix)
    
    # Extract diagonal using validated size
    diagonal = [matrix[i][i] for i in range(size)]
    non_negative = all(value >= 0 for value in diagonal)

    score = 100.0
    score -= min(sym_error * 100, 40.0)
    if not non_negative:
        score -= 40.0

    status = "ok" if score >= 80 else "warning" if score >= 50 else "invalid"

    return {
        "status": status,
        "score": round(max(score, 0.0), 2),
        "symmetry_error": sym_error,
        "non_negative_diagonal": non_negative,
        "matrix_size": len(matrix),
    }


def load_matrix(path: str | Path | None) -> list[list[float]]:
    if path is None:
        return [[1.0, 0.1], [0.1, 1.0]]
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data.get("matrix", data)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run covariance health checks")
    parser.add_argument("--input")
    parser.add_argument("--out", default="docs/wave_packages/runtime/covariance_runtime_report.json")
    args = parser.parse_args(argv)

    report = covariance_health(load_matrix(args.input))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
