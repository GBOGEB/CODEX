from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BackendResidual:
    backend_a: str
    backend_b: str
    delta_h: float
    delta_s: float
    delta_rho: float
    delta_cp: float
    scientific_confidence: float


class BackendComparisonEngine:
    """Scientific convergence scaffold for backend comparison.

    Target backends:
    - internal fallback
    - CoolProp
    - REFPROP
    - HEPAK
    - NIST references
    - GISTAU fixtures
    """

    def compare(self) -> list[BackendResidual]:
        return [
            BackendResidual(
                backend_a='fallback',
                backend_b='nist_reference',
                delta_h=0.12,
                delta_s=0.08,
                delta_rho=0.21,
                delta_cp=0.16,
                scientific_confidence=31.0,
            )
        ]
