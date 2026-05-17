from __future__ import annotations

from .base import State, SaturationState
from .errors import PropertyBackendUnavailable


class CoolPropAdapter:
    """Optional CoolProp backend scaffold.

    Integration target:
    - local repository: GBOGEB/CoolProp
    - upstream project: coolprop.org / CoolProp

    This adapter intentionally avoids a mandatory dependency. The real
    implementation should import CoolProp lazily and preserve fallback behavior
    when CoolProp is unavailable.
    """

    backend_name = "CoolProp"

    def __init__(self):
        try:
            import CoolProp.CoolProp as CP  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency path
            raise PropertyBackendUnavailable(
                "CoolProp is not installed or not importable. "
                "Use FallbackHeliumBackend or install/integrate GBOGEB/CoolProp."
            ) from exc

        self._cp = CP

    def state_pt(self, fluid: str, p_kpa: float, t_k: float) -> State:
        p_pa = p_kpa * 1000.0
        h = self._cp.PropsSI("H", "P", p_pa, "T", t_k, fluid)
        s = self._cp.PropsSI("S", "P", p_pa, "T", t_k, fluid)
        rho = self._cp.PropsSI("D", "P", p_pa, "T", t_k, fluid)
        return State(
            pressure_kpa=p_kpa,
            temperature_k=t_k,
            enthalpy_j_kg=h,
            entropy_j_kgk=s,
            density_kg_m3=rho,
            quality=None,
        )

    def state_ph(self, fluid: str, p_kpa: float, h_j_kg: float) -> State:
        p_pa = p_kpa * 1000.0
        t = self._cp.PropsSI("T", "P", p_pa, "H", h_j_kg, fluid)
        return self.state_pt(fluid, p_kpa, t)

    def state_ps(self, fluid: str, p_kpa: float, s_j_kgk: float) -> State:
        p_pa = p_kpa * 1000.0
        t = self._cp.PropsSI("T", "P", p_pa, "S", s_j_kgk, fluid)
        return self.state_pt(fluid, p_kpa, t)

    def saturation_t(self, fluid: str, t_k: float) -> SaturationState:
        p_pa = self._cp.PropsSI("P", "T", t_k, "Q", 0, fluid)
        rho_l = self._cp.PropsSI("D", "T", t_k, "Q", 0, fluid)
        rho_v = self._cp.PropsSI("D", "T", t_k, "Q", 1, fluid)
        return SaturationState(
            pressure_kpa=p_pa / 1000.0,
            temperature_k=t_k,
            liquid_density_kg_m3=rho_l,
            vapor_density_kg_m3=rho_v,
        )

    def saturation_p(self, fluid: str, p_kpa: float) -> SaturationState:
        p_pa = p_kpa * 1000.0
        t = self._cp.PropsSI("T", "P", p_pa, "Q", 0, fluid)
        rho_l = self._cp.PropsSI("D", "P", p_pa, "Q", 0, fluid)
        rho_v = self._cp.PropsSI("D", "P", p_pa, "Q", 1, fluid)
        return SaturationState(
            pressure_kpa=p_kpa,
            temperature_k=t,
            liquid_density_kg_m3=rho_l,
            vapor_density_kg_m3=rho_v,
        )

    def quality_ph(self, fluid: str, p_kpa: float, h_j_kg: float):
        p_pa = p_kpa * 1000.0
        q = self._cp.PropsSI("Q", "P", p_pa, "H", h_j_kg, fluid)
        if q < 0.0 or q > 1.0:
            return None
        return q
