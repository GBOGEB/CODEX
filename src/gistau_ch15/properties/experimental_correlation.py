from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class ExperimentalCorrelationRow:
    experiment_id: str
    tuple_id: str
    backend_name: str
    measured_value: float
    predicted_value: float
    absolute_residual: float
    relative_residual_percent: float
    quantity: str
    notes: str = ""


class ExperimentalCorrelation:
    """Correlation utilities for cryogenic validation campaigns.

    This module prepares the repository for:
    - publication reproduction,
    - experimental cryogenic comparison,
    - low-temperature correlation campaigns,
    - compressor and JT validation.
    """

    def compare(
        self,
        experiment_id: str,
        tuple_id: str,
        backend_name: str,
        quantity: str,
        measured_value: float,
        predicted_value: float,
        notes: str = "",
    ) -> ExperimentalCorrelationRow:
        absolute_residual = predicted_value - measured_value

        if abs(measured_value) < 1e-12:
            relative = 0.0
        else:
            relative = absolute_residual / measured_value * 100.0

        return ExperimentalCorrelationRow(
            experiment_id=experiment_id,
            tuple_id=tuple_id,
            backend_name=backend_name,
            measured_value=measured_value,
            predicted_value=predicted_value,
            absolute_residual=absolute_residual,
            relative_residual_percent=relative,
            quantity=quantity,
            notes=notes,
        )

    @staticmethod
    def as_dict(row: ExperimentalCorrelationRow) -> dict[str, Any]:
        return asdict(row)
