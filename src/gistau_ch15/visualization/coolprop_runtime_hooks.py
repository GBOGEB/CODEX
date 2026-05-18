from __future__ import annotations

from gistau_ch15.properties.coolprop_adapter import CoolPropAdapter
from gistau_ch15.properties.errors import PropertyBackendUnavailable


class CoolPropRuntimeHooks:
    """Optional CoolProp visualization integration boundary.

    This layer keeps CoolProp optional while providing a stable integration
    point for future generated saturation curves and T-s trajectories.
    """

    def adapter(self) -> CoolPropAdapter:
        return CoolPropAdapter()

    def available(self) -> bool:
        try:
            self.adapter()
            return True
        except PropertyBackendUnavailable:
            return False
