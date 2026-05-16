"""Chapter 15 calculator utilities with version metadata support."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Union

PathLike = Union[str, Path]


@dataclass(frozen=True)
class CalculatorVersion:
    """Version metadata attached to calculator outputs."""

    version: str
    git: str | None = None
    generated_at: str | None = None


def load_version(version_file: PathLike = "VERSION.json") -> CalculatorVersion:
    """Load version metadata from a VERSION.json-like file."""

    data = json.loads(Path(version_file).read_text(encoding="utf-8"))
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
