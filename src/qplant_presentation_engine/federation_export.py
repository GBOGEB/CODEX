"""Canonical federation telemetry artifact export for ABACUS dashboard runtime."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .federation_rollup import FederationRollup, MEMBERS as FEDERATION_MEMBERS
from .federation_scree import FederationScree


class FederationExportError(Exception):
    """Raised when federation artifact export fails."""


class FederationArtifactExporter:
    """Export federation rollup, scree, and bottleneck artifacts."""

    def __init__(self, members: tuple[str, ...] = FEDERATION_MEMBERS) -> None:
        self.members = members

    def _load_repo_metrics(self, metrics_dir: Path) -> dict[str, dict[str, Any]]:
        loaded: dict[str, dict[str, Any]] = {}
        for member in self.members:
            path = metrics_dir / f"{member.lower()}_metrics.json"
            if not path.exists():
                raise FederationExportError(f"Repository metrics file missing for {member}: {path}")
            loaded[member] = json.loads(path.read_text(encoding="utf-8"))
        return loaded

    @staticmethod
    def _metrics(repo_data: dict[str, Any]) -> dict[str, Any]:
        return repo_data.get("metrics", repo_data)  # type: ignore[return-value]

    def build_federation_rollup_export(
        self,
        repo_metrics: dict[str, dict[str, Any]],
        wave: str = "W007",
        subwave: str = "W007.2A",
    ) -> dict[str, Any]:
        rollup = FederationRollup()
        aggregated = rollup.aggregate(repo_metrics)
        repo_summaries: list[dict[str, Any]] = []
        for member in self.members:
            repo_data = repo_metrics[member]
            metrics = self._metrics(repo_data)
            try:
                summary = {
                    "member": member,
                    "repo": repo_data.get("repository", f"GBOGEB/{member}"),
                    "forward_pca": float(metrics["forward_pca"]["convergence_score"]),
                    "backward_pca": float(metrics["backward_pca"]["regression_score"]),
                    "geti": float(metrics["geti"]),
                    "pci": float(metrics["pci"]),
                    "expansion_factor": float(metrics["expansion_factor"]),
                }
            except (KeyError, TypeError, ValueError) as exc:
                raise FederationExportError(
                    f"Failed to extract rollup metrics for {member}: {exc}"
                ) from exc
            repo_summaries.append(summary)

        return {
            "wave": wave,
            "subwave": subwave,
            "members": list(self.members),
            "weights": rollup.weights,
            "forward_pca": aggregated["forward_pca"],
            "backward_pca": aggregated["backward_pca"],
            "geti": aggregated["geti"],
            "pci": aggregated["pci"],
            "expansion_factor": aggregated["expansion_factor"],
            "repo_summaries": repo_summaries,
            "aggregated": aggregated,
        }

    def build_federation_scree_export(
        self,
        repo_metrics: dict[str, dict[str, Any]],
        wave: str = "W007",
        subwave: str = "W007.2A",
    ) -> dict[str, Any]:
        scree = FederationScree()
        aggregated = scree.aggregate_scree(repo_metrics)
        ranked = scree.rank_components(aggregated)
        cumulative = scree.cumulative_variance(aggregated)

        pc_entries: dict[str, dict[str, Any]] = {}
        scree_components: list[dict[str, Any]] = []
        for rank, (component, variance) in enumerate(ranked, start=1):
            component_name = component.upper()
            entry = {
                "variance": round(float(variance), 6),
                "rank": rank,
                "cumulative_variance": round(float(cumulative[component]), 6),
            }
            pc_entries[component_name] = entry
            scree_components.append({"component": component_name, **entry})

        return {
            "wave": wave,
            "subwave": subwave,
            "members": list(self.members),
            "weights": scree.weights,
            **pc_entries,
            "scree_components": scree_components,
            "federation_scree": aggregated,
            "ranked_components": [
                {"component": c, "variance_explained": v} for c, v in ranked
            ],
            "cumulative_variance": cumulative,
        }

    def build_bottleneck_report(
        self,
        repo_metrics: dict[str, dict[str, Any]],
        wave: str = "W007",
        subwave: str = "W007.2A",
        threshold_factor: float = 0.9,
    ) -> dict[str, Any]:
        rollup = FederationRollup()
        aggregated = rollup.aggregate(repo_metrics)
        computed = rollup.compute_bottleneck(repo_metrics, aggregated, threshold_factor=threshold_factor)
        bottlenecks = computed["bottlenecks"]

        if bottlenecks:
            dominant = max(
                bottlenecks,
                key=lambda row: (len(row.get("flags", [])), float(row.get("weight", 0.0))),
            )
            dominant_repo = str(dominant["member"])
            dominant_bottleneck = str((dominant.get("flags") or ["unknown"])[0])
            recommended_next_action = (
                f"Prioritize {dominant_repo} remediation on {dominant_bottleneck}, "
                "then regenerate federation artifacts."
            )
        else:
            dominant_repo = "NONE"
            dominant_bottleneck = "none"
            recommended_next_action = "No bottlenecks detected; continue federation monitoring cadence."

        return {
            "dominant_repo": dominant_repo,
            "dominant_wave": subwave,
            "dominant_bottleneck": dominant_bottleneck,
            "recommended_next_action": recommended_next_action,
            "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "bottleneck_count": int(computed["bottleneck_count"]),
            "bottlenecks": bottlenecks,
            "threshold_factor": threshold_factor,
            "wave": wave,
            "subwave": subwave,
        }

    def write_outputs(
        self,
        metrics_dir: Path,
        federation_dir: Path,
        bottleneck_output: Path,
        wave: str = "W007",
        subwave: str = "W007.2A",
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        if set(self.members) != set(FEDERATION_MEMBERS):
            raise FederationExportError(
                f"write_outputs() requires the canonical federation member set "
                f"{sorted(FEDERATION_MEMBERS)}, got {sorted(self.members)}"
            )
        repo_metrics = self._load_repo_metrics(metrics_dir)
        rollup_record = self.build_federation_rollup_export(repo_metrics, wave=wave, subwave=subwave)
        scree_record = self.build_federation_scree_export(repo_metrics, wave=wave, subwave=subwave)
        bottleneck_record = self.build_bottleneck_report(repo_metrics, wave=wave, subwave=subwave)

        federation_dir.mkdir(parents=True, exist_ok=True)
        bottleneck_output.parent.mkdir(parents=True, exist_ok=True)

        (federation_dir / "federation_rollup.json").write_text(
            json.dumps(rollup_record, indent=2),
            encoding="utf-8",
        )
        (federation_dir / "federation_scree.json").write_text(
            json.dumps(scree_record, indent=2),
            encoding="utf-8",
        )
        bottleneck_output.write_text(json.dumps(bottleneck_record, indent=2), encoding="utf-8")

        return rollup_record, scree_record, bottleneck_record


def generate_federation_artifacts(
    metrics_dir: Path | None = None,
    federation_dir: Path | None = None,
    bottleneck_output: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Generate canonical federation telemetry export artifacts."""
    root = Path(__file__).resolve().parents[2]
    resolved_metrics_dir = metrics_dir or (root / "metrics" / "repo")
    resolved_federation_dir = federation_dir or (root / "metrics" / "federation")
    resolved_bottleneck_output = bottleneck_output or (root / "bottleneck_report.json")
    return FederationArtifactExporter().write_outputs(
        metrics_dir=resolved_metrics_dir,
        federation_dir=resolved_federation_dir,
        bottleneck_output=resolved_bottleneck_output,
    )
