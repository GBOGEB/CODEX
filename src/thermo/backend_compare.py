from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BackendResidual:
    """Backend comparison residual structure.
    
    Fields represent absolute differences between two backends:
    - delta_h: enthalpy difference (J/kg)
    - delta_s: entropy difference (J/kg·K)
    - delta_rho: density difference (kg/m³)
    - delta_cp: specific heat difference (J/kg·K)
    - scientific_confidence: confidence score in range [0, 100]
      where 0 = no confidence, 100 = full confidence
    """
    backend_a: str
    backend_b: str
    delta_h: float  # J/kg
    delta_s: float  # J/kg·K
    delta_rho: float  # kg/m³
    delta_cp: float  # J/kg·K
    scientific_confidence: float  # [0, 100]


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
