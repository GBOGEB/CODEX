from __future__ import annotations

from typing import Any, Optional

from .base import State, SaturationState
from .errors import PropertyBackendUnavailable


class HEPAKAdapter:
    """Optional HEPAK backend scaffold.

    Intended future scope:
    - helium below 5 K,
    - saturated helium,
    - wetness fraction,
    - lambda-region awareness,
    - VLP return analysis,
    - cold-compressor validation.

    This layer remains optional so repository CI can execute without HEPAK.
    """

    backend_name = "HEPAK"

    def __init__(self, fluid: str = "Helium", binding: Any | None = None) -> None:
        self.fluid = fluid
        if binding is not None:
            self._binding = binding
            return
        try:
            import hepak as hepak_binding  # type: ignore
        except Exception as exc:
            raise PropertyBackendUnavailable(
                "HEPAK bindings are not importable. Configure HEPAK before enabling 2 K validation."
            ) from exc
        self._binding = hepak_binding

    def _unavailable(self, call_name: str):
        raise PropertyBackendUnavailable(
            f"HEPAK unavailable for {call_name}. Configure HEPAK bindings before enabling 2 K validation."
        )

    def state_pt(self, fluid: str, p_kpa: float, t_k: float) -> State:
        try:
            raw = self._binding.state_pt(fluid, p_kpa, t_k)
        except Exception as exc:  # pragma: no cover - optional backend path
            raise PropertyBackendUnavailable(f"HEPAK state_pt failed: {exc}") from exc
        return self._to_state(raw, p_kpa, t_k)

    def state_ph(self, fluid: str, p_kpa: float, h_j_kg: float) -> State:
        try:
            raw = self._binding.state_ph(fluid, p_kpa, h_j_kg)
        except Exception as exc:  # pragma: no cover - optional backend path
            raise PropertyBackendUnavailable(f"HEPAK state_ph failed: {exc}") from exc
        return self._to_state(raw, p_kpa, None)

    def state_ps(self, fluid: str, p_kpa: float, s_j_kgk: float) -> State:
        try:
            raw = self._binding.state_ps(fluid, p_kpa, s_j_kgk)
        except Exception as exc:  # pragma: no cover - optional backend path
            raise PropertyBackendUnavailable(f"HEPAK state_ps failed: {exc}") from exc
        return self._to_state(raw, p_kpa, None)

    def saturation_t(self, fluid: str, t_k: float) -> SaturationState:
        try:
            raw = self._binding.saturation_t(fluid, t_k)
        except Exception as exc:  # pragma: no cover - optional backend path
            raise PropertyBackendUnavailable(f"HEPAK saturation_t failed: {exc}") from exc
        return self._to_saturation(raw, None, t_k)

    def saturation_p(self, fluid: str, p_kpa: float) -> SaturationState:
        try:
            raw = self._binding.saturation_p(fluid, p_kpa)
        except Exception as exc:  # pragma: no cover - optional backend path
            raise PropertyBackendUnavailable(f"HEPAK saturation_p failed: {exc}") from exc
        return self._to_saturation(raw, p_kpa, None)

    def quality_ph(self, fluid: str, p_kpa: float, h_j_kg: float) -> Optional[float]:
        try:
            quality = self._binding.quality_ph(fluid, p_kpa, h_j_kg)
        except Exception as exc:  # pragma: no cover - optional backend path
            raise PropertyBackendUnavailable(f"HEPAK quality_ph failed: {exc}") from exc
        return self._bounded_quality(quality)

    @staticmethod
    def _bounded_quality(quality: Any) -> Optional[float]:
        if quality is None:
            return None
        value = float(quality)
        if 0.0 <= value <= 1.0:
            return value
        return None

    def _to_state(self, raw: Any, p_kpa: float, t_k: float | None) -> State:
        if isinstance(raw, State):
            quality = self._bounded_quality(raw.quality)
            return State(
                pressure_kpa=float(raw.pressure_kpa),
                temperature_k=float(raw.temperature_k),
                enthalpy_j_kg=float(raw.enthalpy_j_kg),
                entropy_j_kgk=float(raw.entropy_j_kgk),
                density_kg_m3=float(raw.density_kg_m3),
                quality=quality,
            )
        if isinstance(raw, dict):
            quality = self._bounded_quality(raw.get("quality"))
            return State(
                pressure_kpa=float(raw.get("pressure_kpa", p_kpa)),
                temperature_k=float(raw.get("temperature_k", t_k if t_k is not None else 0.0)),
                enthalpy_j_kg=float(raw["enthalpy_j_kg"]),
                entropy_j_kgk=float(raw["entropy_j_kgk"]),
                density_kg_m3=float(raw["density_kg_m3"]),
                quality=quality,
            )
        raise PropertyBackendUnavailable("HEPAK returned unsupported state payload")

    def _to_saturation(self, raw: Any, p_kpa: float | None, t_k: float | None) -> SaturationState:
        if isinstance(raw, SaturationState):
            return SaturationState(
                pressure_kpa=float(raw.pressure_kpa),
                temperature_k=float(raw.temperature_k),
                liquid_density_kg_m3=float(raw.liquid_density_kg_m3),
                vapor_density_kg_m3=float(raw.vapor_density_kg_m3),
            )
        if isinstance(raw, dict):
            return SaturationState(
                pressure_kpa=float(raw.get("pressure_kpa", p_kpa if p_kpa is not None else 0.0)),
                temperature_k=float(raw.get("temperature_k", t_k if t_k is not None else 0.0)),
                liquid_density_kg_m3=float(raw["liquid_density_kg_m3"]),
                vapor_density_kg_m3=float(raw["vapor_density_kg_m3"]),
            )
        raise PropertyBackendUnavailable("HEPAK returned unsupported saturation payload")

    def validate_two_phase_region(self, state: State) -> dict[str, object]:
        quality = state.quality
        return {
            "backend_name": self.backend_name,
            "quality": quality,
            "two_phase_region": quality is not None and 0.0 <= quality <= 1.0,
            "near_2k_region": state.temperature_k <= 5.0,
        }
