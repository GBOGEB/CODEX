"""Federation scree analysis: PC1–PC5 variance explained across member repositories.

Members: ABACUS, ARTSTYLE, QPLANT, CODEX
Components: pc1, pc2, pc3, pc4, pc5
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MEMBERS: tuple[str, ...] = ("ABACUS", "ARTSTYLE", "QPLANT", "CODEX")
COMPONENTS: tuple[str, ...] = ("pc1", "pc2", "pc3", "pc4", "pc5")
DEFAULT_WEIGHTS: dict[str, float] = {
    "ABACUS": 0.35,
    "ARTSTYLE": 0.20,
    "QPLANT": 0.25,
    "CODEX": 0.20,
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
    ) -> dict[str, Any]:
        """Build the full scree record for federation output (not yet written to disk)."""
        aggregated = self.aggregate_scree(repo_metrics)
        ranked = self.rank_components(aggregated)
        cumulative = self.cumulative_variance(aggregated)
        per_member = {
            member: self._get_scree(repo_metrics[member])
            for member in MEMBERS
            if member in repo_metrics
        }
        return {
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

    def write_scree(
        self,
        repo_metrics: dict[str, dict[str, Any]],
        output_path: Path,
    ) -> dict[str, Any]:
        """Write ``federation_scree.json`` to *output_path* and return the record.

        Parent directories are created if they do not exist.
        """
        record = self.build_scree_record(repo_metrics)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        return record
