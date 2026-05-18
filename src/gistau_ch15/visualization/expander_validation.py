from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ExpanderValidationPoint:
    station: str
    temperature_k: float
    pressure_kpa: float


class FallbackExpanderValidation:
    """Deterministic cryogenic expander validation scaffold."""

    def build(self) -> list[ExpanderValidationPoint]:
        return [
            ExpanderValidationPoint("inlet", 80.0, 1200.0),
            ExpanderValidationPoint("ideal outlet", 22.0, 110.0),
            ExpanderValidationPoint("actual outlet", 32.0, 110.0),
            ExpanderValidationPoint("check point", 32.0, 110.0),
        ]
