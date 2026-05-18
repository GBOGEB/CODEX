from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .base import State, SaturationState
from .errors import PropertyBackendUnavailable


@dataclass(frozen=True)
class REFPROPStatus:
    available: bool
    reason: str


class REFPROPAdapter:
    """Optional REFPROP backend scaffold for canonical helium validation.

    The adapter keeps REFPROP optional and reports unavailable states explicitly.
    Future implementation will bind PT, PH, PS and saturation calls through the
    local REFPROP installation.
    """

    backend_name = "REFPROP"

    def __init__(self, fluid: str = "Helium") -> None:
        self.fluid = fluid
        self.status = REFPROPStatus(
            available=False,
            reason="REFPROP bindings are not configured in this execution environment",
        )

    def _unavailable(self, call_name: str):
        raise PropertyBackendUnavailable(f"REFPROP unavailable for {call_name}: {self.status.reason}")

    def state_pt(self, fluid: str, p_kpa: float, t_k: float) -> State:
        self._unavailable("state_pt")

    def state_ph(self, fluid: str, p_kpa: float, h_j_kg: float) -> State:
        self._unavailable("state_ph")

    def state_ps(self, fluid: str, p_kpa: float, s_j_kgk: float) -> State:
        self._unavailable("state_ps")

    def saturation_t(self, fluid: str, t_k: float) -> SaturationState:
        self._unavailable("saturation_t")

    def saturation_p(self, fluid: str, p_kpa: float) -> SaturationState:
        self._unavailable("saturation_p")

    def quality_ph(self, fluid: str, p_kpa: float, h_j_kg: float) -> Optional[float]:
        self._unavailable("quality_ph")

    def verify_helium_gas_region(self, state: State) -> dict[str, object]:
        return {
            "backend_name": self.backend_name,
            "fluid": self.fluid,
            "pressure_kpa": state.pressure_kpa,
            "temperature_k": state.temperature_k,
            "quality": state.quality,
            "gas_region": state.quality is None or state.quality >= 1.0,
            "status": "ok" if state.quality is None or state.quality >= 1.0 else "non_gas_region",
        }
