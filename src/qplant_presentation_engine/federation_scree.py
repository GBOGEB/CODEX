"""Federation scree analysis: PC1–PC5 variance explained across member repositories.

Members: ABACUS, ARTSTYLE, QPLANT, CODEX, GEMINI, ANTHROPIC
Components: pc1, pc2, pc3, pc4, pc5
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MEMBERS: tuple[str, ...] = ("ABACUS", "ARTSTYLE", "QPLANT", "CODEX", "GEMINI", "ANTHROPIC")
COMPONENTS: tuple[str, ...] = ("pc1", "pc2", "pc3", "pc4", "pc5")
DEFAULT_WEIGHTS: dict[str, float] = {
    "ABACUS": 0.28,
    "ARTSTYLE": 0.16,
    "QPLANT": 0.20,
    "CODEX": 0.16,
    "GEMINI": 0.10,
    "ANTHROPIC": 0.10,
}
_RUNTIME_FILENAMES: dict[str, str] = {
    "ABACUS": "abacus_runtime.json",
    "ARTSTYLE": "artstyle_runtime.json",
    "QPLANT": "qplant_runtime.json",
    "CODEX": "codex_runtime.json",
    "GEMINI": "gemini_runtime.json",
    "ANTHROPIC": "anthropic_runtime.json",
}


class FederationScreeError(Exception):
    """Raised when scree analysis fails."""


class FederationScree:
    """Scree component analysis for federation metrics.

    Extracts PC1–PC5 variance-explained values from per-repository metrics and
    produces a weighted federation-level scree record.

    Parameters
    ----------
    weights:
        Per-member weight mapping.  Defaults to ``DEFAULT_WEIGHTS``.
    """

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights: dict[str, float] = dict(weights) if weights is not None else dict(DEFAULT_WEIGHTS)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_scree(repo_data: dict[str, Any]) -> dict[str, float]:
        metrics = repo_data.get("metrics", repo_data)
        scree = metrics.get("scree")
        if not isinstance(scree, dict):
            raise FederationScreeError(
                "Missing or invalid 'scree' key in repository metrics"
            )
        return scree  # type: ignore[return-value]

    @staticmethod
    def _load_runtime_registry_dir(runtime_registry_dir: Path) -> dict[str, dict[str, Any]]:
        records: dict[str, dict[str, Any]] = {}
        for member, filename in _RUNTIME_FILENAMES.items():
            path = runtime_registry_dir / filename
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except FileNotFoundError as exc:
                raise FederationScreeError(
                    f"Missing runtime artifact for {member}: {path}"
                ) from exc
            except json.JSONDecodeError as exc:
                raise FederationScreeError(
                    f"Invalid JSON in runtime artifact for {member}: {path}"
                ) from exc
            if not isinstance(payload, dict):
                raise FederationScreeError(
                    f"Runtime artifact must be an object for {member}: {path}"
                )
            records[member] = payload
        return records

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def aggregate_scree(
        self,
        repo_metrics: dict[str, dict[str, Any]],
    ) -> dict[str, float]:
        """Compute weighted average scree components across federation members.

        Parameters
        ----------
        repo_metrics:
            Mapping from member name to its metrics dict.

        Returns
        -------
        dict
            ``{"pc1": float, "pc2": float, ..., "pc5": float}``
        """
        for member in MEMBERS:
            if member not in repo_metrics:
                raise FederationScreeError(f"Missing metrics for member: {member}")

        result: dict[str, float] = {c: 0.0 for c in COMPONENTS}
        for member in MEMBERS:
            scree = self._get_scree(repo_metrics[member])
            w = self.weights.get(member, 0.0)
            for component in COMPONENTS:
                result[component] += w * float(scree.get(component, 0.0))
        return {k: round(v, 6) for k, v in result.items()}

    def rank_components(
        self,
        scree: dict[str, float],
    ) -> list[tuple[str, float]]:
        """Return components sorted by variance explained (descending).

        Parameters
        ----------
        scree:
            Scree dict (e.g. from ``aggregate_scree``).

        Returns
        -------
        list of (component_name, variance_explained) tuples
        """
        return sorted(scree.items(), key=lambda x: x[1], reverse=True)

    def cumulative_variance(
        self,
        scree: dict[str, float],
    ) -> dict[str, float]:
        """Return cumulative variance explained in ranked order.

        Parameters
        ----------
        scree:
            Scree dict (e.g. from ``aggregate_scree``).

        Returns
        -------
        dict
            Component names mapped to their cumulative variance explained
            (in descending-variance order).
        """
        ranked = self.rank_components(scree)
        cumulative: dict[str, float] = {}
        total = 0.0
        for name, value in ranked:
            total += value
            cumulative[name] = round(total, 6)
        return cumulative

    def build_scree_record(
        self,
        repo_metrics: dict[str, dict[str, Any]],
        wave: str = "W007",
        subwave: str = "W007.1",
        runtime_records: dict[str, dict[str, Any]] | None = None,
        runtime_registry_dir: Path | None = None,
    ) -> dict[str, Any]:
        """Build the full scree record for federation output (not yet written to disk)."""
        if runtime_records is None and runtime_registry_dir is not None:
            runtime_records = self._load_runtime_registry_dir(runtime_registry_dir)

        aggregated = self.aggregate_scree(repo_metrics)
        ranked = self.rank_components(aggregated)
        cumulative = self.cumulative_variance(aggregated)
        per_member = {
            member: self._get_scree(repo_metrics[member])
            for member in MEMBERS
            if member in repo_metrics
        }
        record = {
            "wave": wave,
            "subwave": subwave,
            "members": list(MEMBERS),
            "weights": self.weights,
            "federation_scree": aggregated,
            "ranked_components": [
                {"component": c, "variance_explained": v} for c, v in ranked
            ],
            "cumulative_variance": cumulative,
            "per_member_scree": per_member,
        }
        if runtime_records is not None:
            truth_matrix = self.build_truth_matrix(runtime_records)
            record["runtime_registry"] = runtime_records
            record["truth_matrix"] = truth_matrix
            record["runtime_status"] = self.build_runtime_status(truth_matrix)
        return record

    def build_runtime_status(self, truth_matrix: list[dict[str, Any]]) -> dict[str, Any]:
        runtime_exists_count = sum(int(entry["runtime_exists"]) for entry in truth_matrix)
        runtime_validated_count = sum(int(entry["runtime_validated"]) for entry in truth_matrix)
        deployment_exists_count = sum(int(entry["deployment_exists"]) for entry in truth_matrix)
        execution_count = sum(int(entry["executed"]) for entry in truth_matrix)
        weighted_truth_score = round(
            sum(self.weights[entry["member"]] * float(entry["truth_score"]) for entry in truth_matrix),
            6,
        )
        return {
            "runtime_exists": runtime_exists_count == len(MEMBERS),
            "runtime_validated": runtime_validated_count == len(MEMBERS),
            "deployment_exists": deployment_exists_count == len(MEMBERS),
            "runtime_exists_count": runtime_exists_count,
            "execution_count": execution_count,
            "runtime_validated_count": runtime_validated_count,
            "deployment_exists_count": deployment_exists_count,
            "weighted_truth_score": weighted_truth_score,
        }

    @staticmethod
    def build_truth_matrix(
        runtime_records: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Return runtime truth-state view aligned to scree members."""
        truth_matrix: list[dict[str, Any]] = []
        for member in MEMBERS:
            if member not in runtime_records:
                raise FederationScreeError(f"Missing runtime record for member: {member}")
            record = runtime_records[member]
            raw_score = record.get("truth_score", 0.0)
            try:
                truth_score = round(float(raw_score), 6)
            except (TypeError, ValueError) as exc:
                raise FederationScreeError(
                    f"Field truth_score must be numeric for {record.get('repo', member)}: {raw_score!r}"
                ) from exc
            truth_matrix.append(
                {
                    "member": member,
                    "repo": record.get("repo", member),
                    "runtime_exists": bool(record.get("runtime_exists")),
                    "executed": bool(record.get("last_execution")),
                    "runtime_validated": bool(record.get("runtime_validated")),
                    "deployment_exists": bool(record.get("deployment_exists")),
                    "truth_score": truth_score,
                }
            )
        return truth_matrix

    def write_scree(
        self,
        repo_metrics: dict[str, dict[str, Any]],
        output_path: Path,
        runtime_records: dict[str, dict[str, Any]] | None = None,
        runtime_registry_dir: Path | None = None,
    ) -> dict[str, Any]:
        """Write ``federation_scree.json`` to *output_path* and return the record.

        Parent directories are created if they do not exist.
        """
        record = self.build_scree_record(
            repo_metrics,
            runtime_records=runtime_records,
            runtime_registry_dir=runtime_registry_dir,
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        return record
