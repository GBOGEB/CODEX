from __future__ import annotations

from gistau_ch15.properties.errors import PropertyBackendUnavailable


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
