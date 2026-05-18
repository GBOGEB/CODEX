from __future__ import annotations

from .errors import PropertyBackendUnavailable


class REFPROPAdapter:
    """Optional REFPROP adapter scaffold.

    REFPROP is the canonical engineering backend for general helium gas-region
    calculations, but it must remain optional so CI and static review builds do
    not fail when REFPROP is unavailable.
    """

    backend_name = "REFPROP"

    def __init__(self) -> None:
        raise PropertyBackendUnavailable(
            "REFPROP backend is not installed or configured in this environment"
        )

    def state_pt(self, pressure: float, temperature: float):
        raise PropertyBackendUnavailable(
            "REFPROP backend is not installed or configured in this environment"
        )

    def state_ph(self, pressure: float, enthalpy: float):
        raise PropertyBackendUnavailable(
            "REFPROP backend is not installed or configured in this environment"
        )

    def state_ps(self, pressure: float, entropy: float):
        raise PropertyBackendUnavailable(
            "REFPROP backend is not installed or configured in this environment"
        )

    def saturation_t(self, temperature: float):
        raise PropertyBackendUnavailable(
            "REFPROP backend is not installed or configured in this environment"
        )

    def saturation_p(self, pressure: float):
        raise PropertyBackendUnavailable(
            "REFPROP backend is not installed or configured in this environment"
        )

    def quality_ph(self, pressure: float, enthalpy: float):
        raise PropertyBackendUnavailable(
            "REFPROP backend is not installed or configured in this environment"
        )
