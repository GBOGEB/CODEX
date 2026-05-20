from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .compare import PropertyDelta
from gistau_ch15.validation.worked_example_runner import WorkedExampleRunner

EXCLUDED_HEATMAP_STATUSES = {"backend_unavailable", "mapping_pending", "reference_unavailable"}


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

    def run_worked_example_comparisons(
        self,
        backends: dict[str, Any],
        availability: list[Any],
        worked_example_runner: WorkedExampleRunner | None = None,
    ) -> list[dict[str, Any]]:
        runner = worked_example_runner or WorkedExampleRunner()
        report_rows: list[dict[str, Any]] = []

        for availability_row in availability:
            backend_name = availability_row.name
            if backend_name == "nist_gistau_reference":
                continue

            backend = backends.get(backend_name)
            for output_row in runner.run_for_backend(
                backend_name=backend_name,
                backend_tier=availability_row.tier.value,
                backend=backend,
                backend_available=availability_row.available,
                unavailable_reason=availability_row.reason,
            ):
                report_rows.append(output_row)

        return report_rows

    def build_summary(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "row_count": len(rows),
            "status_counts": self._status_counts(rows),
            "backend_names": sorted({r["backend_name"] for r in rows}),
        }

    def build_heatmap_matrix(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        """Build tuple-indexed temperature-delta matrix.

        Legacy compare.py rows use ``delta_temperature_k`` directly.
        Worked-example rows use ``absolute_delta`` only for the
        ``outlet_temperature_k`` quantity.
        """
        matrix: dict[str, dict[str, float | None]] = {}

        for row in rows:
            if row.get("status") in EXCLUDED_HEATMAP_STATUSES:
                continue
            backend = row["backend_name"]
            matrix.setdefault(backend, {})
            delta_value = None
            if "delta_temperature_k" in row:
                delta_value = row["delta_temperature_k"]
            elif row.get("quantity") == "outlet_temperature_k":
                delta_value = row["absolute_delta"]
            if delta_value is not None:
                matrix[backend][row["tuple_id"]] = delta_value

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
