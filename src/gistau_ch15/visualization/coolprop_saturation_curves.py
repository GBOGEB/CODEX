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
            adapter = hooks.adapter()
            temperatures = [1.8, 2.0, 2.4, 3.0, 3.8, 4.6]

            entropy_liquid = [
                float(adapter._cp.PropsSI("S", "T", t, "Q", 0, "Helium"))
                for t in temperatures
            ]
            entropy_vapor = [
                float(adapter._cp.PropsSI("S", "T", t, "Q", 1, "Helium"))
                for t in temperatures
            ]
        except PropertyBackendUnavailable:
            return FallbackSaturationSampler().sample()
        except Exception:
            return FallbackSaturationSampler().sample()

        return SaturationCurve(
            entropy_liquid=entropy_liquid,
            temperature_liquid=temperatures,
            entropy_vapor=entropy_vapor,
            temperature_vapor=temperatures,
        )
