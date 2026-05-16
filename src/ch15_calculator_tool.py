"""Chapter 15 Calculator Tool with semantic version metadata."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class CalculatorVersion:
    version: str
    git: str | None = None
    generated_at: str | None = None


def load_version(version_file: str = "VERSION.json") -> CalculatorVersion:
    """Load version metadata from VERSION.json."""
    data = json.loads(Path(version_file).read_text(encoding="utf-8"))
    return CalculatorVersion(
        version=data.get("version", "0.0.0"),
        git=data.get("git"),
        generated_at=data.get("generated_at"),
    )


def calculate_total_with_contingency(base_cost: float, contingency_pct: float) -> float:
    """Compute total cost with contingency as percentage."""
    if base_cost < 0:
        raise ValueError("base_cost must be >= 0")
    if contingency_pct < 0:
        raise ValueError("contingency_pct must be >= 0")
    return base_cost * (1 + contingency_pct / 100.0)


def calculate_failure_rate(failures: int, operating_hours: float) -> float:
    """Compute failures per operating hour."""
    if failures < 0:
        raise ValueError("failures must be >= 0")
    if operating_hours <= 0:
        raise ValueError("operating_hours must be > 0")
    return failures / operating_hours
