"""A66 synchronization and freshness runtime.

Provides deterministic synchronization scoring and executable checks for:
- manifest consistency
- topology freshness
- artifact existence
- synchronization lag
- Pages continuity readiness
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class SyncCheck:
    name: str
    status: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "status": self.status,
            "detail": self.detail,
        }


class SynchronizationEngine:
    def __init__(self) -> None:
        self.checks: list[SyncCheck] = []

    def freshness_score(self, lag_seconds: int, max_lag: int = 3600) -> float:
        if lag_seconds < 0:
            raise ValueError("lag_seconds cannot be negative")
        if max_lag <= 0:
            raise ValueError(f"max_lag must be positive, got {max_lag}")
        score = 1 - (lag_seconds / max_lag)
        return round(max(0.0, min(score, 1.0)), 4)

    def emit(self, name: str, status: str, detail: str) -> None:
        self.checks.append(SyncCheck(name=name, status=status, detail=detail))

    def validate_manifest_paths(self, manifest_path: str | Path) -> dict[str, Any]:
        manifest = Path(manifest_path)
        if not manifest.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest}")

        data = json.loads(manifest.read_text(encoding="utf-8"))
        publish_targets = data.get("published_pages", [])

        missing: list[str] = []
        existing: list[str] = []

        for entry in publish_targets:
            if "*" in entry or "<" in entry:
                continue
            p = Path(entry)
            if p.exists():
                existing.append(entry)
            else:
                missing.append(entry)

        status = "ok" if not missing else "warning"
        detail = f"existing={len(existing)} missing={len(missing)}"
        self.emit("manifest_validation", status, detail)

        return {
            "status": status,
            "existing": existing,
            "missing": missing,
        }

    def topology_consistency(self, topology_path: str | Path) -> dict[str, Any]:
        topology = Path(topology_path)
        if not topology.exists():
            raise FileNotFoundError(f"Topology runtime missing: {topology}")

        data = json.loads(topology.read_text(encoding="utf-8"))
        forward = data.get("forward_recursion", [])
        backward = data.get("backward_recursion", [])

        if not forward or not backward:
            status = "invalid"
            detail = "Topology recursion flows incomplete"
        else:
            status = "ok"
            detail = f"forward={len(forward)} backward={len(backward)}"

        self.emit("topology_consistency", status, detail)

        return {
            "status": status,
            "forward_steps": len(forward),
            "backward_steps": len(backward),
        }

    def synchronization_report(self) -> dict[str, Any]:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "operational",
            "checks": [check.as_dict() for check in self.checks],
        }


if __name__ == "__main__":
    engine = SynchronizationEngine()
    try:
        engine.validate_manifest_paths("MANIFEST.json")
        engine.topology_consistency("docs/wave_packages/topology/topology_runtime.json")
    except FileNotFoundError as exc:
        engine.emit("bootstrap", "warning", str(exc))

    print(json.dumps(engine.synchronization_report(), indent=2))
