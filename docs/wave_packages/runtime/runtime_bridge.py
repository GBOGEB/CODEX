"""A66 runtime bridge orchestration.

This module turns the A66 bridge scaffold into a deterministic, executable
handover/runtime runner. It intentionally avoids network side effects: Pages
publication and autonomous rebuilds are emitted as explicit action records so
CI or a later GitHub Actions workflow can execute them safely.

Forward flow:
ABACUS feed -> schema validation -> KPI federation -> topology synchronization
-> CODEX hydration -> Pages regeneration plan.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

REQUIRED_PAYLOAD_KEYS = ("source", "wave", "artifacts")
DEFAULT_TOPOLOGY_PATH = Path("docs/wave_packages/topology/topology_runtime.json")
DEFAULT_REPORT_PATH = Path("docs/wave_packages/runtime/runtime_bridge_report.json")


@dataclass
class BridgeEvent:
    """Single runtime event emitted by the bridge."""

    stage: str
    status: str
    detail: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def as_dict(self) -> dict[str, str]:
        return {
            "stage": self.stage,
            "status": self.status,
            "detail": self.detail,
            "timestamp": self.timestamp,
        }


class RuntimeBridge:
    """Executable orchestration bridge for A66 regeneration continuity."""

    def __init__(self, topology_path: str | Path = DEFAULT_TOPOLOGY_PATH):
        self.topology_path = Path(topology_path)
        self.events: list[BridgeEvent] = []
        self.feed_registry: dict[str, Any] = {}
        self.topology: dict[str, Any] = {}

    def emit(self, stage: str, status: str, detail: str) -> None:
        self.events.append(BridgeEvent(stage=stage, status=status, detail=detail))

    def load_feed_manifest(self, path: str | Path) -> dict[str, Any]:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Feed manifest not found: {p}")
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Feed manifest must be a JSON object")
        self.feed_registry = data
        self.emit("feed_manifest", "ok", f"Loaded feed manifest from {p}")
        return data

    def load_topology(self) -> dict[str, Any]:
        if not self.topology_path.exists():
            raise FileNotFoundError(f"Topology runtime not found: {self.topology_path}")
        data = json.loads(self.topology_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Topology runtime must be a JSON object")
        self.topology = data
        self.emit("topology", "ok", f"Loaded topology runtime from {self.topology_path}")
        return data

    def validate_schema(self, payload: dict[str, Any]) -> bool:
        """Validate the minimal A66 bridge payload contract.

        Required keys:
        - source: upstream source name, normally ABACUS or manual_fixture
        - wave: wave identifier, for example A66
        - artifacts: list or object describing runtime artifacts
        """
        missing = [key for key in REQUIRED_PAYLOAD_KEYS if key not in payload]
        if missing:
            raise ValueError(f"Payload missing required keys: {', '.join(missing)}")
        if not isinstance(payload["source"], str) or not payload["source"].strip():
            raise ValueError("Payload key 'source' must be a non-empty string")
        if not isinstance(payload["wave"], str) or not payload["wave"].strip():
            raise ValueError("Payload key 'wave' must be a non-empty string")
        if not isinstance(payload["artifacts"], (list, dict)):
            raise ValueError("Payload key 'artifacts' must be a list or object")
        self.emit("schema_validation", "ok", "Payload satisfies A66 minimal bridge contract")
        return True

    def federate_kpis(self, payload: dict[str, Any]) -> dict[str, Any]:
        metrics = payload.get("metrics", {})
        if metrics and not isinstance(metrics, dict):
            raise ValueError("Optional payload key 'metrics' must be an object")
        federation = {
            "wave": payload["wave"],
            "metric_count": len(metrics),
            "metrics": metrics,
            "status": "federated" if metrics else "no_metrics_supplied",
        }
        self.emit("kpi_federation", "ok", federation["status"])
        return federation

    def hydrate_runtime(self, payload: dict[str, Any], topology: dict[str, Any]) -> dict[str, Any]:
        artifacts = payload["artifacts"]
        artifact_count = len(artifacts) if isinstance(artifacts, (list, dict)) else 0
        hydration = {
            "status": "hydrated",
            "source": payload["source"],
            "wave": payload["wave"],
            "artifact_count": artifact_count,
            "topology_version": topology.get("version"),
            "pages_continuity": topology.get("pages_publication", {}).get("continuity_status", "unknown"),
        }
        self.emit("runtime_hydration", "ok", f"Hydrated {artifact_count} artifact(s)")
        return hydration

    def update_topology(self, payload: dict[str, Any], dry_run: bool = True) -> dict[str, Any]:
        if not self.topology:
            self.load_topology()
        runtime_state = self.topology.setdefault("runtime_state", {})
        runtime_state.update(
            {
                "last_wave": payload["wave"],
                "last_source": payload["source"],
                "last_bridge_run_utc": datetime.now(timezone.utc).isoformat(),
                "dry_run": dry_run,
            }
        )
        self.emit("topology_sync", "ok", "Topology runtime state updated in memory")
        return self.topology

    def trigger_pages_regeneration(self, dry_run: bool = True) -> dict[str, Any]:
        plan = {
            "status": "planned" if dry_run else "requested",
            "dry_run": dry_run,
            "actions": [
                "validate MANIFEST.json",
                "rebuild docs runtime bundle",
                "publish docs/ via GitHub Pages workflow",
                "run post-publish smoke checks",
            ],
        }
        self.emit("pages_regeneration", "ok", plan["status"])
        return plan

    def run(self, payload: dict[str, Any], dry_run: bool = True) -> dict[str, Any]:
        topology = self.load_topology()
        self.validate_schema(payload)
        kpis = self.federate_kpis(payload)
        topology_after = self.update_topology(payload, dry_run=dry_run)
        hydration = self.hydrate_runtime(payload, topology_after)
        pages = self.trigger_pages_regeneration(dry_run=dry_run)
        return {
            "status": "ok",
            "mode": "dry_run" if dry_run else "execution_requested",
            "kpi_federation": kpis,
            "runtime_hydration": hydration,
            "pages_regeneration": pages,
            "events": [event.as_dict() for event in self.events],
        }


def load_payload(path: str | Path | None) -> dict[str, Any]:
    if path is None:
        return {
            "source": "manual_fixture",
            "wave": "A66",
            "artifacts": [
                "docs/wave_packages/runtime/runtime_bridge.py",
                "docs/wave_packages/runtime/synchronization_engine.py",
                "docs/wave_packages/topology/topology_runtime.json",
            ],
            "metrics": {
                "autonomous_regeneration": 72,
                "ci_execution_closure": 82,
                "topology_persistence": 90,
                "pages_continuity": 82,
                "bridge_orchestration": 88,
            },
        }
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8"))


def write_report(report: dict[str, Any], path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the A66 executable runtime bridge")
    parser.add_argument("--payload", help="JSON payload/feed manifest to execute")
    parser.add_argument("--topology", default=str(DEFAULT_TOPOLOGY_PATH), help="Topology runtime JSON path")
    parser.add_argument("--report", default=str(DEFAULT_REPORT_PATH), help="Output report JSON path")
    parser.add_argument("--execute", action="store_true", help="Request execution mode instead of dry-run planning")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    bridge = RuntimeBridge(topology_path=args.topology)
    payload = load_payload(args.payload)
    report = bridge.run(payload, dry_run=not args.execute)
    write_report(report, args.report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
