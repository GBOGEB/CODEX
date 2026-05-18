from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from gistau_ch15.validation.calculation_runner import run_seed_calculation_report


@dataclass(frozen=True)
class BackendComparisonRow:
    example_id: str
    tuple_id: str
    backend_name: str
    backend_tier: str
    reference_tier: str
    quantity: str
    backend_value: float | None
    reference_value: float | None
    absolute_delta: float | None
    relative_delta: float | None
    unit: str
    status: str
    notes: str


def seed_rows_to_backend_comparison() -> list[BackendComparisonRow]:
    """Convert fallback seed calculations into comparison-report rows.

    This is the first executable bridge from calculation_runner.py into the
    GitHub Pages backend heatmap. Later passes will add CoolProp, REFPROP and
    HEPAK rows using the same schema.
    """

    rows: list[BackendComparisonRow] = []
    for item in run_seed_calculation_report():
        rows.append(
            BackendComparisonRow(
                example_id=item["example_id"],
                tuple_id=item["tuple_id"],
                backend_name="fallback",
                backend_tier="tier0_fallback",
                reference_tier="tier4_nist_gistau_reference",
                quantity=item["quantity"],
                backend_value=item["calculated_value"],
                reference_value=item["expected_value"],
                absolute_delta=item["absolute_delta"],
                relative_delta=item["relative_delta"],
                unit=item["unit"],
                status=item["status"],
                notes=item["notes"],
            )
        )
    return rows


def generate_backend_comparison_report() -> list[dict[str, Any]]:
    return [asdict(row) for row in seed_rows_to_backend_comparison()]
