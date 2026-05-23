from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HeliumState:
    temperature_k: float
    pressure_pa: float
    enthalpy_j_kg: float
    entropy_j_kgk: float
    density_kg_m3: float
    cp_j_kgk: float
    cv_j_kgk: float
    gibbs_j_kg: float
    exergy_j_kg: float
    notes: str


class HeliumReferenceKernel:
    """Explicit helium reference-kernel scaffold.

    This is not a substitute for HEPAK, REFPROP or validated NIST tables.
    It is a governed internal kernel boundary for deterministic testing,
    low-temperature scaffolding and backend-comparison plumbing.
    """

    R_HE = 2077.1
    CP_IDEAL = 5193.0
    CV_IDEAL = CP_IDEAL - R_HE

    def state_tp(
        self,
        temperature_k: float,
        pressure_pa: float,
        ambient_temperature_k: float = 300.0,
    ) -> HeliumState:
        h = self.CP_IDEAL * temperature_k
        s = self.CP_IDEAL * max(temperature_k, 1e-9) / max(ambient_temperature_k, 1e-9)
        rho = pressure_pa / (self.R_HE * temperature_k)
        g = h - temperature_k * s
        exergy = h - ambient_temperature_k * s

        return HeliumState(
            temperature_k=temperature_k,
            pressure_pa=pressure_pa,
            enthalpy_j_kg=h,
            entropy_j_kgk=s,
            density_kg_m3=rho,
            cp_j_kgk=self.CP_IDEAL,
            cv_j_kgk=self.CV_IDEAL,
            gibbs_j_kg=g,
            exergy_j_kg=exergy,
            notes='A9 scaffold kernel only; requires NIST/REFPROP/HEPAK validation.',
        )
