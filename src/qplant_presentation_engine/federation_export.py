"""Canonical federation telemetry artifact export for ABACUS dashboard runtime."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .federation_rollup import (
    FederationRollup,
    FederationRollupError,
    MEMBERS as FEDERATION_MEMBERS,
)
from .federation_scree import COMPONENTS as SCREE_COMPONENTS, FederationScree, FederationScreeError


class FederationExportError(Exception):
    """Raised when federation artifact export fails."""


class FederationArtifactExporter:
    """Export federation rollup, scree, and bottleneck artifacts."""

    def __init__(self, members: tuple[str, ...] = FEDERATION_MEMBERS) -> None:
        self.members = members

    def _load_repo_metrics(
        self,
        metrics_dir: Path,
        members: tuple[str, ...] | None = None,
    ) -> dict[str, dict[str, Any]]:
        ordered_members = members or self.members
        loaded: dict[str, dict[str, Any]] = {}
        for member in ordered_members:
            path = metrics_dir / f"{member.lower()}_metrics.json"
            if not path.exists():
                raise FederationExportError(f"Repository metrics file missing for {member}: {path}")
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise FederationExportError(
                    f"Invalid repository metrics JSON for {member}: {path}: {exc.msg}"
                ) from exc
            if not isinstance(payload, dict):
                raise FederationExportError(
                    f"Invalid repository metrics payload for {member}: {path}: expected JSON object"
                )
            loaded[member] = payload
        return loaded

    @staticmethod
    def _metrics(repo_data: dict[str, Any]) -> dict[str, Any]:
        return repo_data.get("metrics", repo_data)  # type: ignore[return-value]

    @staticmethod
    def _validate_numeric(value: Any, field_name: str, member: str) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise FederationExportError(f"Invalid {field_name} for {member}: expected numeric value")
        return float(value)

    def _validate_rollup_member_metrics(self, member: str, repo_data: dict[str, Any]) -> None:
        metrics = self._metrics(repo_data)
        if not isinstance(metrics, dict):
            raise FederationExportError(f"Invalid metrics payload for {member}: expected object")
        for field_name, pca_key, score_key in (
            ("forward_pca", "forward_pca", "convergence_score"),
            ("backward_pca", "backward_pca", "regression_score"),
        ):
            pca = metrics.get(pca_key)
            if not isinstance(pca, dict):
                raise FederationExportError(f"Invalid {field_name} for {member}: expected object")
            variance = pca.get("variance_explained")
            if (
                not isinstance(variance, list)
                or len(variance) != 5
                or any(isinstance(component, bool) or not isinstance(component, (int, float)) for component in variance)
            ):
                raise FederationExportError(
                    f"Invalid {field_name}.variance_explained for {member}: expected 5 numeric values"
                )
            self._validate_numeric(pca.get(score_key), f"{field_name}.{score_key}", member)
        for field_name in ("geti", "pci", "expansion_factor"):
            self._validate_numeric(metrics.get(field_name), field_name, member)

    def _validate_scree_member_metrics(self, member: str, repo_data: dict[str, Any]) -> None:
        metrics = self._metrics(repo_data)
        if not isinstance(metrics, dict):
            raise FederationExportError(f"Invalid metrics payload for {member}: expected object")
        scree = metrics.get("scree")
        if not isinstance(scree, dict):
            raise FederationExportError(f"Invalid scree for {member}: expected object")
        for component in SCREE_COMPONENTS:
            self._validate_numeric(scree.get(component), f"scree.{component}", member)

    def build_federation_rollup_export(
        self,
        repo_metrics: dict[str, dict[str, Any]],
        wave: str = "W007",
        subwave: str = "W007.2A",
        members: tuple[str, ...] | None = None,
    ) -> dict[str, Any]:
        ordered_members = members or self.members
        rollup = FederationRollup()
        repo_summaries: list[dict[str, Any]] = []
        for member in ordered_members:
            repo_data = repo_metrics[member]
            self._validate_rollup_member_metrics(member, repo_data)
            metrics = self._metrics(repo_data)
            try:
                conv_score = self._validate_numeric(
                    metrics["forward_pca"]["convergence_score"], "forward_pca.convergence_score", member
                )
                reg_score = self._validate_numeric(
                    metrics["backward_pca"]["regression_score"], "backward_pca.regression_score", member
                )
                geti_val = self._validate_numeric(metrics["geti"], "geti", member)
                pci_val = self._validate_numeric(metrics["pci"], "pci", member)
                exp_factor = self._validate_numeric(metrics["expansion_factor"], "expansion_factor", member)
                summary = {
                    "member": member,
                    "repo": repo_data.get("repository", f"GBOGEB/{member}"),
                    "forward_pca": conv_score,
                    "backward_pca": reg_score,
                    "geti": geti_val,
                    "pci": pci_val,
                    "expansion_factor": exp_factor,
                }
            except (KeyError, TypeError, ValueError) as exc:
                raise FederationExportError(
                    f"Failed to extract rollup metrics for {member}: {exc}"
                ) from exc
            repo_summaries.append(summary)
        try:
            aggregated = rollup.aggregate(repo_metrics)
        except (FederationRollupError, KeyError, TypeError, ValueError) as exc:
            raise FederationExportError(f"Failed to aggregate federation rollup: {exc}") from exc

        return {
            "wave": wave,
            "subwave": subwave,
            "members": list(ordered_members),
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
        members: tuple[str, ...] | None = None,
    ) -> dict[str, Any]:
        ordered_members = members or self.members
        scree = FederationScree()
        for member in ordered_members:
            self._validate_scree_member_metrics(member, repo_metrics[member])
        try:
            aggregated = scree.aggregate_scree(repo_metrics)
            ranked = scree.rank_components(aggregated)
            cumulative = scree.cumulative_variance(aggregated)
        except (FederationScreeError, KeyError, TypeError, ValueError) as exc:
            raise FederationExportError(f"Failed to aggregate federation scree: {exc}") from exc

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
            "members": list(ordered_members),
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
        generated_at: str | None = None,
    ) -> dict[str, Any]:
        rollup = FederationRollup()
        try:
            aggregated = rollup.aggregate(repo_metrics)
            computed = rollup.compute_bottleneck(repo_metrics, aggregated, threshold_factor=threshold_factor)
        except (FederationRollupError, KeyError, TypeError, ValueError) as exc:
            raise FederationExportError(f"Failed to build bottleneck report: {exc}") from exc
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
            "timestamp": generated_at if generated_at is not None else datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
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
        generated_at: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        if set(self.members) != set(FEDERATION_MEMBERS) or len(self.members) != len(FEDERATION_MEMBERS):
            raise FederationExportError(
                f"write_outputs() requires exactly the canonical federation members "
                f"{sorted(FEDERATION_MEMBERS)} (in any order), got {sorted(self.members)}"
            )
        canonical_members = FEDERATION_MEMBERS
        repo_metrics = self._load_repo_metrics(metrics_dir, members=canonical_members)
        rollup_record = self.build_federation_rollup_export(
            repo_metrics,
            wave=wave,
            subwave=subwave,
            members=canonical_members,
        )
        scree_record = self.build_federation_scree_export(
            repo_metrics,
            wave=wave,
            subwave=subwave,
            members=canonical_members,
        )
        bottleneck_record = self.build_bottleneck_report(
            repo_metrics, wave=wave, subwave=subwave, generated_at=generated_at
        )

        federation_dir.mkdir(parents=True, exist_ok=True)
        bottleneck_output.parent.mkdir(parents=True, exist_ok=True)

        (federation_dir / "federation_rollup.json").write_text(
            json.dumps(rollup_record, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (federation_dir / "federation_scree.json").write_text(
            json.dumps(scree_record, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        bottleneck_output.write_text(json.dumps(bottleneck_record, indent=2, sort_keys=True), encoding="utf-8")

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
