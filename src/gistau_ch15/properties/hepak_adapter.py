from __future__ import annotations

from gistau_ch15.properties.base import State, SaturationState
from gistau_ch15.properties.errors import PropertyBackendUnavailable


class HEPAKAdapter:
    """Optional HEPAK backend adapter scaffold.

    The adapter is intentionally unavailable until a local HEPAK bridge is
    configured. This keeps CI deterministic while preserving the interface for
    future low-temperature helium validation.
    """

    backend_name = "HEPAK"

    def __init__(self) -> None:
        raise PropertyBackendUnavailable("HEPAK runtime bridge is not configured")

    def state_pt(self, fluid: str, p_kpa: float, t_k: float) -> State:
        raise PropertyBackendUnavailable("HEPAK state_pt binding pending")

    def state_ph(self, fluid: str, p_kpa: float, h_j_kg: float) -> State:
        raise PropertyBackendUnavailable("HEPAK state_ph binding pending")

    def state_ps(self, fluid: str, p_kpa: float, s_j_kgk: float) -> State:
        raise PropertyBackendUnavailable("HEPAK state_ps binding pending")

    def saturation_t(self, fluid: str, t_k: float) -> SaturationState:
        raise PropertyBackendUnavailable("HEPAK saturation_t binding pending")

    def saturation_p(self, fluid: str, p_kpa: float) -> SaturationState:
        raise PropertyBackendUnavailable("HEPAK saturation_p binding pending")

    def quality_ph(self, fluid: str, p_kpa: float, h_j_kg: float):
        raise PropertyBackendUnavailable("HEPAK quality_ph binding pending")
