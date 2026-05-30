"""Runtime registry loading utilities for federation member repositories."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RUNTIME_REGISTRY_FILES: dict[str, str] = {
    "ABACUS": "abacus_runtime.json",
    "ARTSTYLE": "artstyle_runtime.json",
    "QPLANT": "qplant_runtime.json",
    "CODEX": "codex_runtime.json",
}
REQUIRED_RUNTIME_FIELDS: set[str] = {
    "repo",
    "runtime_exists",
    "runtime_validated",
    "deployment_exists",
    "last_execution",
    "last_validation",
    "last_deployment",
    "truth_score",
}


def default_runtime_registry_dir() -> Path:
    """Return the repository default runtime registry directory."""
    return Path(__file__).resolve().parents[2] / "federation" / "runtime_registry"


def load_runtime_registry(runtime_registry_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    """Load runtime registry evidence records from JSON files."""
    registry_dir = runtime_registry_dir or default_runtime_registry_dir()
    records: dict[str, dict[str, Any]] = {}
    for member, filename in RUNTIME_REGISTRY_FILES.items():
        path = registry_dir / filename
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        missing = REQUIRED_RUNTIME_FIELDS - set(data.keys())
        if missing:
            raise ValueError(f"Runtime registry file missing keys {sorted(missing)}: {path}")
        records[member] = data
    return records


def summarize_runtime_registry(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return an aggregate runtime status summary."""
    if not records:
        return {}
    count = len(records)
    truth_score = sum(float(record["truth_score"]) for record in records.values()) / count
    return {
        "repositories": count,
        "runtime_exists": all(bool(record["runtime_exists"]) for record in records.values()),
        "runtime_validated": all(bool(record["runtime_validated"]) for record in records.values()),
        "deployment_exists": all(bool(record["deployment_exists"]) for record in records.values()),
        "average_truth_score": round(truth_score, 6),
    }
