from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .base import State, SaturationState
from .errors import PropertyBackendUnavailable


@dataclass(frozen=True)
class REFPROPStatus:
    available: bool
    reason: str


class REFPROPAdapter:
    """Optional REFPROP backend for canonical helium validation.

    The implementation imports ctREFPROP lazily and keeps REFPROP optional.
    Missing bindings or library paths are reported through PropertyBackendUnavailable
    instead of breaking fallback/CoolProp CI execution.
    """

    backend_name = "REFPROP"

    def __init__(self, fluid: str = "Helium", root_path: str | None = None) -> None:
        self.fluid = fluid
        self.root_path = root_path or ""
        self._rp: Any | None = None
        self._molar_mass_g_mol: dict[str, float] = {}
        self.status = REFPROPStatus(False, "REFPROP not loaded")
        self._load()

    def _load(self) -> Any:
        if self._rp is not None:
            return self._rp
        try:
            import ctREFPROP.ctREFPROP as ctrefprop  # type: ignore
        except Exception as exc:
            self.status = REFPROPStatus(False, "ctREFPROP is not importable")
            raise PropertyBackendUnavailable(self.status.reason) from exc
        try:
            self._rp = ctrefprop.REFPROPFunctionLibrary(self.root_path)
            self.status = REFPROPStatus(True, "available")
            return self._rp
        except Exception as exc:
            self.status = REFPROPStatus(False, "REFPROP library could not be initialized")
            raise PropertyBackendUnavailable(self.status.reason) from exc

    @staticmethod
    def _fluid_name(fluid: str) -> str:
        if fluid.lower() in {"he", "helium", "helium4", "helium-4"}:
            return "HELIUM"
        return fluid.upper()

    def _call(self, fluid: str, inputs: str, output: str, x1: float, x2: float) -> float:
        rp = self._load()
        name = self._fluid_name(fluid or self.fluid)
        try:
            result = rp.REFPROPdll(name, inputs, output, 0, 0, 0, x1, x2, [1.0])
        except Exception as exc:
            raise PropertyBackendUnavailable(f"REFPROP call failed: {inputs} to {output}") from exc
        if getattr(result, "ierr", 0):
            raise PropertyBackendUnavailable(str(getattr(result, "herr", "REFPROP error")))
        return float(result.Output[0])

    def _molar_mass(self, fluid: str) -> float:
        name = self._fluid_name(fluid or self.fluid)
        if name not in self._molar_mass_g_mol:
            self._molar_mass_g_mol[name] = self._call(name, "TP", "W", 300.0, 101.325)
        return self._molar_mass_g_mol[name]

    def _h_or_s_molar_to_mass(self, value_j_mol: float, fluid: str) -> float:
        return value_j_mol * (1000.0 / self._molar_mass(fluid))

    def _h_or_s_mass_to_molar(self, value_j_kg: float, fluid: str) -> float:
        return value_j_kg * (self._molar_mass(fluid) / 1000.0)

    def _density_molar_to_mass(self, value_mol_l: float, fluid: str) -> float:
        # mol/L * g/mol == g/L == kg/m3
        return value_mol_l * self._molar_mass(fluid)

    def state_pt(self, fluid: str, p_kpa: float, t_k: float) -> State:
        h = self._h_or_s_molar_to_mass(self._call(fluid, "TP", "H", t_k, p_kpa), fluid)
        s = self._h_or_s_molar_to_mass(self._call(fluid, "TP", "S", t_k, p_kpa), fluid)
        rho = self._density_molar_to_mass(self._call(fluid, "TP", "D", t_k, p_kpa), fluid)
        return State(p_kpa, t_k, h, s, rho, self._quality_or_none(fluid, "TP", t_k, p_kpa))

    def state_ph(self, fluid: str, p_kpa: float, h_j_kg: float) -> State:
        h_j_mol = self._h_or_s_mass_to_molar(h_j_kg, fluid)
        t = self._call(fluid, "PH", "T", p_kpa, h_j_mol)
        s = self._h_or_s_molar_to_mass(self._call(fluid, "PH", "S", p_kpa, h_j_mol), fluid)
        rho = self._density_molar_to_mass(self._call(fluid, "PH", "D", p_kpa, h_j_mol), fluid)
        return State(p_kpa, t, h_j_kg, s, rho, self._quality_or_none(fluid, "PH", p_kpa, h_j_mol))

    def state_ps(self, fluid: str, p_kpa: float, s_j_kgk: float) -> State:
        s_j_molk = self._h_or_s_mass_to_molar(s_j_kgk, fluid)
        t = self._call(fluid, "PS", "T", p_kpa, s_j_molk)
        h = self._h_or_s_molar_to_mass(self._call(fluid, "PS", "H", p_kpa, s_j_molk), fluid)
        rho = self._density_molar_to_mass(self._call(fluid, "PS", "D", p_kpa, s_j_molk), fluid)
        return State(p_kpa, t, h, s_j_kgk, rho, self._quality_or_none(fluid, "PS", p_kpa, s_j_molk))

    def saturation_t(self, fluid: str, t_k: float) -> SaturationState:
        p = self._call(fluid, "TQ", "P", t_k, 0.0)
        rho_l = self._density_molar_to_mass(self._call(fluid, "TQ", "D", t_k, 0.0), fluid)
        rho_v = self._density_molar_to_mass(self._call(fluid, "TQ", "D", t_k, 1.0), fluid)
        return SaturationState(p, t_k, rho_l, rho_v)

    def saturation_p(self, fluid: str, p_kpa: float) -> SaturationState:
        t = self._call(fluid, "PQ", "T", p_kpa, 0.0)
        rho_l = self._density_molar_to_mass(self._call(fluid, "PQ", "D", p_kpa, 0.0), fluid)
        rho_v = self._density_molar_to_mass(self._call(fluid, "PQ", "D", p_kpa, 1.0), fluid)
        return SaturationState(p_kpa, t, rho_l, rho_v)

    def quality_ph(self, fluid: str, p_kpa: float, h_j_kg: float) -> Optional[float]:
        return self._quality_or_none(fluid, "PH", p_kpa, self._h_or_s_mass_to_molar(h_j_kg, fluid))

    def _quality_or_none(self, fluid: str, inputs: str, x1: float, x2: float) -> Optional[float]:
        try:
            q = self._call(fluid, inputs, "Q", x1, x2)
        except Exception:
            return None
        return q if 0.0 <= q <= 1.0 else None

    def verify_helium_gas_region(self, state: State) -> dict[str, object]:
        gas_region = state.quality is None or state.quality >= 1.0
        return {
            "backend_name": self.backend_name,
            "fluid": self.fluid,
            "pressure_kpa": state.pressure_kpa,
            "temperature_k": state.temperature_k,
            "quality": state.quality,
            "gas_region": gas_region,
            "status": "ok" if gas_region else "non_gas_region",
        }
