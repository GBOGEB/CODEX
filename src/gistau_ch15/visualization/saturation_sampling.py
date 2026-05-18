from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SaturationCurve:
    entropy_liquid: list[float]
    temperature_liquid: list[float]
    entropy_vapor: list[float]
    temperature_vapor: list[float]


class FallbackSaturationSampler:
    """Deterministic saturation scaffold.

    Future PRs will replace or augment this with:

    - CoolProp generated curves
    - REFPROP canonical overlays
    - HEPAK low-temperature helium surfaces
    """

    def sample(self) -> SaturationCurve:
        return SaturationCurve(
            entropy_liquid=[5, 12, 20, 31, 45, 62],
            temperature_liquid=[1.8, 2.0, 2.4, 3.0, 3.8, 4.6],
            entropy_vapor=[450, 390, 330, 270, 220, 180],
            temperature_vapor=[1.8, 2.0, 2.4, 3.0, 3.8, 4.6],
        )
