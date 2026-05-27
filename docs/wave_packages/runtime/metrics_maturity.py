"""A67 maturity, progress, and DMAIC runtime metrics.

Computes deterministic completion statistics from runtime status data. The
module has no external dependencies and can run in local development, CI, or
Pages-generation preparation.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DEFAULT_STATUS = {
    "autonomous_regeneration": {"previous": 61, "current": 72, "target": 100, "dmaic": "Improve"},
    "ci_execution_closure": {"previous": 74, "current": 82, "target": 100, "dmaic": "Control"},
    "topology_persistence": {"previous": 85, "current": 90, "target": 100, "dmaic": "Control"},
    "pages_continuity": {"previous": 73, "current": 82, "target": 100, "dmaic": "Improve"},
    "bridge_orchestration": {"previous": 79, "current": 88, "target": 100, "dmaic": "Control"},
    "synchronization": {"previous": 63, "current": 91, "target": 100, "dmaic": "Control"},
    "covariance_runtime": {"previous": 45, "current": 60, "target": 100, "dmaic": "Analyze"},
    "abacus_feed_ingestion": {"previous": 30, "current": 52, "target": 100, "dmaic": "Improve"},
    "self_healing_runtime": {"previous": 35, "current": 48, "target": 100, "dmaic": "Analyze"},
}

DMAIC_ORDER = ["Define", "Measure", "Analyze", "Improve", "Control"]


@dataclass(frozen=True)
class CapabilityScore:
    name: str
    previous: float
    current: float
    target: float
    dmaic: str

    @property
    def delta(self) -> float:
        return round(self.current - self.previous, 2)

    @property
    def remaining(self) -> float:
        return round(max(self.target - self.current, 0), 2)

    @property
    def completion_ratio(self) -> float:
        return round(self.current / self.target, 4) if self.target > 0 else 0.0

    @property
    def maturity_band(self) -> str:
        if self.current >= 90:
            return "operational-high"
        if self.current >= 80:
            return "operational-medium-high"
        if self.current >= 65:
            return "executable-scaffold"
        if self.current >= 50:
            return "partial-runtime"
        return "conceptual-weak-runtime"

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "previous": self.previous,
            "current": self.current,
            "target": self.target,
            "delta": self.delta,
            "remaining": self.remaining,
            "completion_ratio": self.completion_ratio,
            "completion_percent": round(self.completion_ratio * 100, 2),
            "maturity_band": self.maturity_band,
            "dmaic": self.dmaic,
        }


def load_status(path: str | Path | None = None) -> dict:
    if path is None:
        return DEFAULT_STATUS
    return json.loads(Path(path).read_text(encoding="utf-8"))


def compute_scores(status: dict) -> list[CapabilityScore]:
    scores: list[CapabilityScore] = []
    for name, values in sorted(status.items()):
        scores.append(
            CapabilityScore(
                name=name,
                previous=float(values.get("previous", 0)),
                current=float(values.get("current", 0)),
                target=float(values.get("target", 100)),
                dmaic=str(values.get("dmaic", "Measure")),
            )
        )
    return scores


def maturity_distribution(scores: list[CapabilityScore]) -> dict[str, int]:
    distribution: dict[str, int] = {}
    for score in scores:
        distribution[score.maturity_band] = distribution.get(score.maturity_band, 0) + 1
    return distribution


def dmaic_summary(scores: list[CapabilityScore]) -> dict:
    summary = {phase: {"count": 0, "average_current": 0.0} for phase in DMAIC_ORDER}
    for phase in DMAIC_ORDER:
        values = [score.current for score in scores if score.dmaic == phase]
        summary[phase] = {
            "count": len(values),
            "average_current": round(sum(values) / len(values), 2) if values else 0.0,
        }
    return summary


def build_report(status: dict) -> dict:
    scores = compute_scores(status)
    average_current = round(sum(score.current for score in scores) / len(scores), 2) if scores else 0.0
    average_delta = round(sum(score.delta for score in scores) / len(scores), 2) if scores else 0.0
    high_debt = sorted(scores, key=lambda item: item.remaining, reverse=True)[:5]
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "runtime-maturity-report",
        "average_completion_percent": average_current,
        "average_delta_percent": average_delta,
        "capability_count": len(scores),
        "fully_complete_count": len([score for score in scores if score.current >= score.target]),
        "maturity_distribution": maturity_distribution(scores),
        "dmaic_summary": dmaic_summary(scores),
        "highest_remaining_debt": [score.as_dict() for score in high_debt],
        "capabilities": [score.as_dict() for score in scores],
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Runtime Maturity and DMAIC Report",
        "",
        f"Generated: `{report['timestamp']}`",
        f"Average completion: **{report['average_completion_percent']}%**",
        f"Average uplift: **{report['average_delta_percent']} points**",
        "",
        "## Capability Scores",
        "",
        "| Capability | Previous | Current | Delta | Remaining | Maturity | DMAIC |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for item in report["capabilities"]:
        lines.append(
            f"| {item['name']} | {item['previous']} | {item['current']} | {item['delta']} | {item['remaining']} | {item['maturity_band']} | {item['dmaic']} |"
        )
    lines.extend(["", "## Highest Remaining Debt", ""])
    lines.extend(
        f"- {item['name']}: {item['remaining']} points remaining ({item['dmaic']})"
        for item in report["highest_remaining_debt"]
    )
    lines.append("")
    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate runtime maturity and DMAIC metrics")
    parser.add_argument("--input", help="Optional JSON status registry")
    parser.add_argument("--json-out", default="docs/wave_packages/runtime/runtime_maturity_report.json")
    parser.add_argument("--md-out", default="docs/wave_packages/runtime/runtime_maturity_report.md")
    args = parser.parse_args(argv)

    report = build_report(load_status(args.input))
    json_path = Path(args.json_out)
    md_path = Path(args.md_out)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
