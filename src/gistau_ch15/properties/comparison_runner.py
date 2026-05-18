from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .compare import PropertyDelta


class ComparisonRunner:
    """Publication-grade backend delta aggregation scaffold.

    Planned outputs:
    - backend_comparison_report.json
    - backend_delta_summary.json
    - backend_heatmap_matrix.json
    """

    def build_rows(self, deltas: list[PropertyDelta]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []

        for delta in deltas:
            rows.append(
                {
                    "example_id": delta.request_id,
                    "tuple_id": delta.tuple_id,
                    "backend_name": delta.backend_name,
                    "backend_tier": delta.tier.value,
                    "reference_backend": delta.reference_backend,
                    "delta_temperature_k": delta.delta_temperature_k,
                    "delta_enthalpy_j_kg": delta.delta_enthalpy_j_kg,
                    "delta_entropy_j_kgk": delta.delta_entropy_j_kgk,
                    "delta_density_kg_m3": delta.delta_density_kg_m3,
                    "status": delta.status,
                }
            )

        return rows

    def build_summary(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "row_count": len(rows),
            "status_counts": self._status_counts(rows),
            "backend_names": sorted({r["backend_name"] for r in rows}),
        }

    def build_heatmap_matrix(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        matrix: dict[str, dict[str, float | None]] = {}

        for row in rows:
            backend = row["backend_name"]
            matrix.setdefault(backend, {})
            matrix[backend][row["tuple_id"]] = row["delta_temperature_k"]

        return matrix

    @staticmethod
    def serialize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [asdict(r) if hasattr(r, "__dataclass_fields__") else r for r in rows]

    @staticmethod
    def _status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for row in rows:
            status = row["status"]
            counts[status] = counts.get(status, 0) + 1
        return counts
