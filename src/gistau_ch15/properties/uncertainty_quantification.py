from __future__ import annotations

from dataclasses import dataclass, asdict
from math import sqrt
from typing import Any, Iterable


@dataclass(frozen=True)
class UncertaintyResult:
    quantity: str
    backend_name: str
    mean_value: float
    standard_deviation: float
    relative_uncertainty_percent: float
    sample_count: int


class UncertaintyQuantification:
    """Numerical uncertainty quantification utilities.

    Intended future usage:
    - REFPROP vs HEPAK divergence,
    - low-temperature uncertainty maps,
    - publication uncertainty envelopes,
    - experimental correlation residual analysis.
    """

    def summarize(
        self,
        quantity: str,
        backend_name: str,
        values: Iterable[float],
    ) -> UncertaintyResult:
        samples = list(values)
        if not samples:
            raise ValueError("values must not be empty")

        mean_value = sum(samples) / len(samples)
        variance = sum((v - mean_value) ** 2 for v in samples) / len(samples)
        std_dev = sqrt(variance)

        if abs(mean_value) < 1e-12:
            relative = 0.0
        else:
            relative = abs(std_dev / mean_value) * 100.0

        return UncertaintyResult(
            quantity=quantity,
            backend_name=backend_name,
            mean_value=mean_value,
            standard_deviation=std_dev,
            relative_uncertainty_percent=relative,
            sample_count=len(samples),
        )

    @staticmethod
    def as_dict(result: UncertaintyResult) -> dict[str, Any]:
        return asdict(result)
