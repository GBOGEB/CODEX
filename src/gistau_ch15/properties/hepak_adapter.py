from __future__ import annotations

from gistau_ch15.properties.errors import PropertyBackendUnavailable


class HEPAKAdapter:
    """Optional HEPAK adapter scaffold.

    HEPAK is expected to become the preferred backend for:

    - helium below 5 K,
    - two-phase helium,
    - quality/wetness calculations,
    - VLP return regions,
    - near-2 K saturation checks.

    This scaffold keeps the interface explicit while remaining CI-safe.
    """

    backend_name = "HEPAK"

    def __init__(self) -> None:
        raise PropertyBackendUnavailable(
            "HEPAK backend is not installed or not connected"
        )

    def state_pt(self, pressure, temperature):
        raise PropertyBackendUnavailable(
            "HEPAK backend is not installed or not connected"
        )

    def state_ph(self, pressure, enthalpy):
        raise PropertyBackendUnavailable(
            "HEPAK backend is not installed or not connected"
        )

    def state_ps(self, pressure, entropy):
        raise PropertyBackendUnavailable(
            "HEPAK backend is not installed or not connected"
        )

    def saturation_t(self, temperature):
        raise PropertyBackendUnavailable(
            "HEPAK backend is not installed or not connected"
        )

    def saturation_p(self, pressure):
        raise PropertyBackendUnavailable(
            "HEPAK backend is not installed or not connected"
        )

    def quality_ph(self, pressure, enthalpy):
        raise PropertyBackendUnavailable(
            "HEPAK backend is not installed or not connected"
        )
