from __future__ import annotations

from typing import Any

from gistau_ch15.properties.base import State, SaturationState
from gistau_ch15.properties.errors import PropertyBackendUnavailable


class REFPROPAdapter:
    """Optional REFPROP backend adapter scaffold.

    REFPROP is the canonical engineering backend for gas-region helium
    verification and workbook reproduction. This scaffold defines the adapter
    boundary without making REFPROP a CI dependency.
    """

    backend_name = "REFPROP"

    def __init__(self) -> None:
        try:
            import ctREFPROP.ctREFPROP as ct  # type: ignore
        except Exception as exc:  # pragma: no cover - optional licensed dependency
            raise PropertyBackendUnavailable(
                "REFPROP is not installed or not importable. Install ctREFPROP "
                "and configure REFPROP before enabling canonical verification."
            ) from exc

        # The concrete REFPROP root path and library binding are installation
        # specific. Keep a handle to the module so local deployments can extend
        # this adapter without changing selector/report semantics.
        self._ct: Any = ct
        raise PropertyBackendUnavailable(
            "REFPROP adapter scaffold is present, but runtime binding is not yet configured."
        )

    def state_pt(self, fluid: str, p_kpa: float, t_k: float) -> State:
        raise PropertyBackendUnavailable("REFPROP state_pt binding pending")

    def state_ph(self, fluid: str, p_kpa: float, h_j_kg: float) -> State:
        raise PropertyBackendUnavailable("REFPROP state_ph binding pending")

    def state_ps(self, fluid: str, p_kpa: float, s_j_kgk: float) -> State:
        raise PropertyBackendUnavailable("REFPROP state_ps binding pending")

    def saturation_t(self, fluid: str, t_k: float) -> SaturationState:
        raise PropertyBackendUnavailable("REFPROP saturation_t binding pending")

    def saturation_p(self, fluid: str, p_kpa: float) -> SaturationState:
        raise PropertyBackendUnavailable("REFPROP saturation_p binding pending")

    def quality_ph(self, fluid: str, p_kpa: float, h_j_kg: float):
        raise PropertyBackendUnavailable("REFPROP quality_ph binding pending")
