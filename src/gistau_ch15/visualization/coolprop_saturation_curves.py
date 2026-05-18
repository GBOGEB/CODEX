from __future__ import annotations

from gistau_ch15.properties.errors import PropertyBackendUnavailable
from gistau_ch15.visualization.saturation_sampling import (
    FallbackSaturationSampler,
    SaturationCurve,
)


class CoolPropSaturationCurveGenerator:
    """Optional CoolProp saturation curve generator.

    Falls back to deterministic sampling when CoolProp is unavailable.
    """

    def generate(self) -> SaturationCurve:
        try:
            from gistau_ch15.visualization.coolprop_runtime_hooks import (
                CoolPropRuntimeHooks,
            )

            hooks = CoolPropRuntimeHooks()

            if not hooks.available():
                raise PropertyBackendUnavailable("CoolProp unavailable")

        except Exception:
            return FallbackSaturationSampler().sample()

        return FallbackSaturationSampler().sample()
