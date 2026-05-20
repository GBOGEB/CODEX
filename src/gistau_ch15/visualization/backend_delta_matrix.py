from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BackendDeltaMatrix:
    backends: list[str]
    enthalpy_delta_pct: list[float]
    density_delta_pct: list[float]
    temperature_delta_k: list[float]


class FallbackBackendDeltaBuilder:
    """Deterministic backend delta scaffold.

    Future implementations will populate these deltas from executable backend
    comparisons and canonical validation references.
    """

    def build(self) -> BackendDeltaMatrix:
        return BackendDeltaMatrix(
            backends=["fallback", "coolprop", "refprop", "hepak"],
            enthalpy_delta_pct=[12.5, 2.1, 0.0, 0.4],
            density_delta_pct=[18.0, 3.2, 0.0, 0.6],
            temperature_delta_k=[1.2, 0.25, 0.0, 0.05],
        )
