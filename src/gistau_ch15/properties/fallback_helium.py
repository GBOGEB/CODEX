from __future__ import annotations

import math

from .base import State, SaturationState

IDEAL_GAS_DOMAIN = "IDEAL_GAS_DOMAIN"
OUTSIDE_IDEAL_GAS_DOMAIN = "OUTSIDE_IDEAL_GAS_DOMAIN"


class FallbackHeliumBackend:
    """Ideal-gas helium-4: the basic incarnation used as a cross-check.

    Role: CROSSCHECK_ONLY. Helium-4 physics is governed by GBOGEB/ABACUS
    (governance/physics/HE4_PROPERTY_AUTHORITY_PIN.yaml); this backend never
    governs and exists so that an independent, simple model can flag drift.

    Model: monatomic ideal gas, cp = 5/2 R.
      rho = p / (R T)
      h   = cp T                                   (h = 0 at T = 0 K)
      s   = cp ln(T / T_REF) - R ln(p / P_REF)     (s = 0 at 300 K, 101.325 kPa)
    Absolute h and s use this backend's own reference state, so compare
    differences (Delta h, Delta s, isentropic paths) with other backends, not
    absolute values.

    Validity: states are tagged IDEAL_GAS_DOMAIN only inside the declared
    domain (T >= DOMAIN_T_MIN_K and p <= DOMAIN_P_MAX_KPA). The bounds are
    provisional until the CI cross-check against the pinned ABACUS provider
    measures the deviation over a grid. Saturation methods are placeholders
    and are outside the cross-check scope.
    """

    R = 2077.1
    CP = 5193.0
    T_REF_K = 300.0
    P_REF_KPA = 101.325
    DOMAIN_T_MIN_K = 20.0
    DOMAIN_P_MAX_KPA = 1000.0
    DOMAIN_STATUS = "PROVISIONAL_PENDING_ABACUS_CROSSCHECK"

    @staticmethod
    def _require_positive(p_kpa: float, t_k: float) -> None:
        if not p_kpa > 0.0:
            raise ValueError(f"pressure must be positive, got {p_kpa} kPa")
        if not t_k > 0.0:
            raise ValueError(f"temperature must be positive, got {t_k} K")

    def in_validity_domain(self, p_kpa: float, t_k: float) -> bool:
        return t_k >= self.DOMAIN_T_MIN_K and p_kpa <= self.DOMAIN_P_MAX_KPA

    def entropy_pt(self, p_kpa: float, t_k: float) -> float:
        self._require_positive(p_kpa, t_k)
        return self.CP * math.log(t_k / self.T_REF_K) - self.R * math.log(p_kpa / self.P_REF_KPA)

    def state_pt(self, fluid: str, p_kpa: float, t_k: float) -> State:
        self._require_positive(p_kpa, t_k)
        return State(
            pressure_kpa=p_kpa,
            temperature_k=t_k,
            enthalpy_j_kg=self.CP * t_k,
            entropy_j_kgk=self.entropy_pt(p_kpa, t_k),
            density_kg_m3=(p_kpa * 1000.0) / (self.R * t_k),
            quality=None,
            validity=IDEAL_GAS_DOMAIN if self.in_validity_domain(p_kpa, t_k) else OUTSIDE_IDEAL_GAS_DOMAIN,
        )

    def state_ph(self, fluid: str, p_kpa: float, h_j_kg: float) -> State:
        return self.state_pt(fluid, p_kpa, h_j_kg / self.CP)

    def state_ps(self, fluid: str, p_kpa: float, s_j_kgk: float) -> State:
        if not p_kpa > 0.0:
            raise ValueError(f"pressure must be positive, got {p_kpa} kPa")
        t_k = self.T_REF_K * math.exp((s_j_kgk + self.R * math.log(p_kpa / self.P_REF_KPA)) / self.CP)
        return self.state_pt(fluid, p_kpa, t_k)

    def saturation_t(self, fluid: str, t_k: float) -> SaturationState:
        # Placeholder, outside the cross-check scope.
        return SaturationState(
            pressure_kpa=max(1.0, t_k * 10.0),
            temperature_k=t_k,
            liquid_density_kg_m3=125.0,
            vapor_density_kg_m3=0.2,
        )

    def saturation_p(self, fluid: str, p_kpa: float) -> SaturationState:
        # Placeholder, outside the cross-check scope.
        return SaturationState(
            pressure_kpa=p_kpa,
            temperature_k=max(1.8, p_kpa / 10.0),
            liquid_density_kg_m3=125.0,
            vapor_density_kg_m3=0.2,
        )

    def quality_ph(self, fluid: str, p_kpa: float, h_j_kg: float):
        return None
