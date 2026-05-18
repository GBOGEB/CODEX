from __future__ import annotations


class PhaseRegionClassifier:
    """Deterministic low-temperature phase classifier scaffold."""

    def classify(self, pressure_kpa: float, temperature_k: float) -> str:
        if temperature_k <= 2.2:
            return "two-phase"

        if temperature_k <= 5.0:
            return "near-saturation"

        return "gas"
