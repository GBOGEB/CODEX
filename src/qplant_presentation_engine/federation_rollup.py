"""Federation metric rollup: weighted aggregation across member repositories.

Members: ABACUS, ARTSTYLE, QPLANT, CODEX

Supported metrics:
  - forward_pca   (convergence_score, variance_explained[5])
  - backward_pca  (regression_score,  variance_explained[5])
  - geti          Governance/Engineering Target Index  [0, 1]
  - pci           Project Completeness Index           [0, 1]
  - expansion_factor
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MEMBERS: tuple[str, ...] = ("ABACUS", "ARTSTYLE", "QPLANT", "CODEX")
DEFAULT_WEIGHTS: dict[str, float] = {
    "ABACUS": 0.35,
    "ARTSTYLE": 0.20,
    "QPLANT": 0.25,
    "CODEX": 0.20,
}
SCALAR_METRICS: tuple[str, ...] = ("geti", "pci", "expansion_factor")
_PCA_SCORE_KEYS: dict[str, str] = {
    "forward_pca": "convergence_score",
    "backward_pca": "regression_score",
}
_N_COMPONENTS = 5


class FederationRollupError(Exception):
    """Raised when federation rollup computation fails."""


class FederationRollup:
    """Weighted aggregation of federation metrics across member repositories.

    Parameters
    ----------
    weights:
        Per-member weight mapping.  Must sum to 1.0 and include all four
        members.  Defaults to ``DEFAULT_WEIGHTS``.
    """

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights: dict[str, float] = dict(weights) if weights is not None else dict(DEFAULT_WEIGHTS)
        self._validate_weights()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_weights(self) -> None:
        total = sum(self.weights.values())
        if abs(total - 1.0) > 1e-6:
            raise FederationRollupError(
                f"Weights must sum to 1.0, got {total:.6f}"
            )
        for member in MEMBERS:
            if member not in self.weights:
                raise FederationRollupError(f"Missing weight for member: {member}")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _metrics(repo_data: dict[str, Any]) -> dict[str, Any]:
        return repo_data.get("metrics", repo_data)  # type: ignore[return-value]

    def _weighted_scalar(
        self,
        repo_metrics: dict[str, dict[str, Any]],
        key: str,
    ) -> float:
        result = 0.0
        for member in MEMBERS:
            value = float(self._metrics(repo_metrics[member])[key])
            result += self.weights[member] * value
        return round(result, 6)

    def _weighted_pca(
        self,
        repo_metrics: dict[str, dict[str, Any]],
        pca_key: str,
        score_key: str,
    ) -> dict[str, Any]:
        variance: list[float] = [0.0] * _N_COMPONENTS
        score = 0.0
        for member in MEMBERS:
            pca = self._metrics(repo_metrics[member])[pca_key]
            w = self.weights[member]
            pca_variance: list[float] = pca["variance_explained"]
            for i in range(min(_N_COMPONENTS, len(pca_variance))):
                variance[i] += w * pca_variance[i]
            score += w * float(pca[score_key])
        return {
            "variance_explained": [round(v, 6) for v in variance],
            score_key: round(score, 6),
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def aggregate(
        self,
        repo_metrics: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Return weighted federation-level aggregated metrics.

        Parameters
        ----------
        repo_metrics:
            Mapping from member name (ABACUS / ARTSTYLE / QPLANT / CODEX)
            to that repository's metrics dict (as loaded from its JSON file).

        Returns
        -------
        dict
            Aggregated scalar and PCA metrics.
        """
        for member in MEMBERS:
            if member not in repo_metrics:
                raise FederationRollupError(f"Missing metrics for member: {member}")

        result: dict[str, Any] = {}
        for key in SCALAR_METRICS:
            result[key] = self._weighted_scalar(repo_metrics, key)
        for pca_key, score_key in _PCA_SCORE_KEYS.items():
            result[pca_key] = self._weighted_pca(repo_metrics, pca_key, score_key)
        return result

    def compute_bottleneck(
        self,
        repo_metrics: dict[str, dict[str, Any]],
        rollup: dict[str, Any],
        threshold_factor: float = 0.9,
    ) -> dict[str, Any]:
        """Identify repositories whose scalar metrics fall below the threshold.

        A member is flagged when its value for a scalar metric is less than
        ``threshold_factor * federation_average``.

        Parameters
        ----------
        repo_metrics:
            Per-member metrics (same format as ``aggregate``).
        rollup:
            Aggregated federation metrics returned by ``aggregate``.
        threshold_factor:
            Fraction of the federation average used as the bottleneck
            threshold (default 0.9).

        Returns
        -------
        dict
            Bottleneck report with a list of flagged members.
        """
        bottlenecks: list[dict[str, Any]] = []
        for member in MEMBERS:
            metrics = self._metrics(repo_metrics[member])
            flags: list[str] = []
            for key in SCALAR_METRICS:
                threshold = rollup[key] * threshold_factor
                if float(metrics[key]) < threshold:
                    flags.append(key)
            if flags:
                bottlenecks.append(
                    {
                        "member": member,
                        "flags": flags,
                        "weight": self.weights[member],
                    }
                )
        return {
            "wave": "W007",
            "subwave": "W007.1",
            "threshold_factor": threshold_factor,
            "bottleneck_count": len(bottlenecks),
            "bottlenecks": bottlenecks,
        }

    def build_rollup_record(
        self,
        repo_metrics: dict[str, dict[str, Any]],
        wave: str = "W007",
        subwave: str = "W007.1",
        runtime_records: dict[str, dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Build the complete rollup record (not yet written to disk)."""
        aggregated = self.aggregate(repo_metrics)
        record = {
            "wave": wave,
            "subwave": subwave,
            "members": list(MEMBERS),
            "weights": self.weights,
            "aggregated": aggregated,
        }
        if runtime_records is not None:
            record["runtime_status"] = self.build_runtime_status(runtime_records)
        return record

    def build_runtime_status(
        self,
        runtime_records: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Build runtime evidence summary for federation members."""
        for member in MEMBERS:
            if member not in runtime_records:
                raise FederationRollupError(f"Missing runtime record for member: {member}")

        truth_matrix: list[dict[str, Any]] = []
        runtime_exists_count = 0
        runtime_validated_count = 0
        deployment_exists_count = 0
        execution_count = 0
        weighted_truth_score = 0.0

        for member in MEMBERS:
            record = runtime_records[member]
            runtime_exists = bool(record.get("runtime_exists"))
            runtime_validated = bool(record.get("runtime_validated"))
            deployment_exists = bool(record.get("deployment_exists"))
            executed = bool(record.get("last_execution"))
            truth_score = float(record.get("truth_score", 0.0))

            runtime_exists_count += int(runtime_exists)
            runtime_validated_count += int(runtime_validated)
            deployment_exists_count += int(deployment_exists)
            execution_count += int(executed)
            weighted_truth_score += self.weights[member] * truth_score

            truth_matrix.append(
                {
                    "member": member,
                    "repo": record.get("repo", member),
                    "runtime_exists": runtime_exists,
                    "executed": executed,
                    "runtime_validated": runtime_validated,
                    "deployment_exists": deployment_exists,
                    "truth_score": round(truth_score, 6),
                }
            )

        return {
            "runtime_exists_count": runtime_exists_count,
            "execution_count": execution_count,
            "runtime_validated_count": runtime_validated_count,
            "deployment_exists_count": deployment_exists_count,
            "weighted_truth_score": round(weighted_truth_score, 6),
            "truth_matrix": truth_matrix,
        }

    def write_rollup(
        self,
        repo_metrics: dict[str, dict[str, Any]],
        output_path: Path,
        runtime_records: dict[str, dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Write ``federation_rollup.json`` to *output_path* and return the record.

        Parent directories are created if they do not exist.
        """
        record = self.build_rollup_record(repo_metrics, runtime_records=runtime_records)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        return record

    def write_bottleneck_report(
        self,
        repo_metrics: dict[str, dict[str, Any]],
        output_path: Path,
        threshold_factor: float = 0.9,
    ) -> dict[str, Any]:
        """Write ``bottleneck_report.json`` to *output_path* and return the report.

        Parent directories are created if they do not exist.
        """
        rollup = self.aggregate(repo_metrics)
        report = self.compute_bottleneck(repo_metrics, rollup, threshold_factor)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report
