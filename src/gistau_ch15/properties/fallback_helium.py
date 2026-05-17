from __future__ import annotations

from .base import State, SaturationState


class FallbackHeliumBackend:
    """Simplified fallback helium backend.

    This backend intentionally uses approximate relationships so the
    engineering portal remains self-contained and operational without
    REFPROP or HEPAK.
    """

    R = 2077.1
    CP = 5193.0

    def state_pt(self, fluid: str, p_kpa: float, t_k: float) -> State:
        rho = (p_kpa * 1000.0) / (self.R * t_k)
        h = self.CP * t_k
        s = self.CP * max(t_k, 1e-9)
        return State(
            pressure_kpa=p_kpa,
            temperature_k=t_k,
            enthalpy_j_kg=h,
            entropy_j_kgk=s,
            density_kg_m3=rho,
            quality=None,
        )

    def state_ph(self, fluid: str, p_kpa: float, h_j_kg: float) -> State:
        t_k = h_j_kg / self.CP
        return self.state_pt(fluid, p_kpa, t_k)

    def state_ps(self, fluid: str, p_kpa: float, s_j_kgk: float) -> State:
        t_k = s_j_kgk / self.CP
        return self.state_pt(fluid, p_kpa, t_k)

    def saturation_t(self, fluid: str, t_k: float) -> SaturationState:
        return SaturationState(
            pressure_kpa=max(1.0, t_k * 10.0),
            temperature_k=t_k,
            liquid_density_kg_m3=125.0,
            vapor_density_kg_m3=0.2,
        )

    def saturation_p(self, fluid: str, p_kpa: float) -> SaturationState:
        return SaturationState(
            pressure_kpa=p_kpa,
            temperature_k=max(1.8, p_kpa / 10.0),
            liquid_density_kg_m3=125.0,
            vapor_density_kg_m3=0.2,
        )

    def quality_ph(self, fluid: str, p_kpa: float, h_j_kg: float):
        return None
