"""Chapter 15 calculator utilities with version metadata support."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Union

PathLike = Union[str, Path]
ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class CalculatorVersion:
    """Version metadata attached to calculator outputs."""

    version: str
    git: str | None = None
    generated_at: str | None = None


@dataclass(frozen=True)
class Ch15InputSample:
    """Input sample for Chapter 15 calculations."""

    base_cost: float
    contingency_pct: float
    failures: int
    operating_hours: float


def load_version(version_file: PathLike | None = None) -> CalculatorVersion:
    """Load version metadata from a VERSION.json-like file."""

    version_path = ROOT / "VERSION.json" if version_file is None else Path(version_file)
    data = json.loads(version_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("VERSION metadata must be a JSON object")
    version = data.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("VERSION metadata must include a non-empty string 'version'")

    return CalculatorVersion(
        version=version,
        git=data.get("git"),
        generated_at=data.get("generated_at"),
    )


def calculate_total_with_contingency(base_cost: float, contingency_pct: float) -> float:
    """Return total cost after contingency percentage is applied."""

    if base_cost < 0:
        raise ValueError("base_cost must be >= 0")
    if contingency_pct < 0:
        raise ValueError("contingency_pct must be >= 0")

    return base_cost * (1.0 + contingency_pct / 100.0)


def calculate_failure_rate(failures: int, operating_hours: float) -> float:
    """Return failures per operating hour."""

    if failures < 0:
        raise ValueError("failures must be >= 0")
    if operating_hours <= 0:
        raise ValueError("operating_hours must be > 0")

    return failures / operating_hours


def load_input_sample(sample_file: PathLike) -> Ch15InputSample:
    """Load a Chapter 15 input sample JSON and validate required fields."""

    data: dict[str, Any] = json.loads(Path(sample_file).read_text(encoding="utf-8"))
    required = ("base_cost", "contingency_pct", "failures", "operating_hours")
    missing = [field for field in required if field not in data]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    sample = Ch15InputSample(
        base_cost=float(data["base_cost"]),
        contingency_pct=float(data["contingency_pct"]),
        failures=int(data["failures"]),
        operating_hours=float(data["operating_hours"]),
    )
    # Reuse validation rules from calculation functions.
    calculate_total_with_contingency(sample.base_cost, sample.contingency_pct)
    calculate_failure_rate(sample.failures, sample.operating_hours)
    return sample


def build_sample_stats(sample: Ch15InputSample) -> dict[str, float]:
    """Compute deterministic output stats for a sample input."""

    total_with_contingency = calculate_total_with_contingency(
        sample.base_cost,
        sample.contingency_pct,
    )
    failure_rate = calculate_failure_rate(sample.failures, sample.operating_hours)

    return {
        "base_cost": sample.base_cost,
        "contingency_pct": sample.contingency_pct,
        "total_with_contingency": total_with_contingency,
        "failures": float(sample.failures),
        "operating_hours": sample.operating_hours,
        "failure_rate_per_hour": failure_rate,
    }
