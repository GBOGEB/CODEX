from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EquivalentPowerResult:
    compressor_power_w: float
    expander_recovery_w: float
    refrigeration_load_w: float
    carnot_factor: float
    equivalent_power_w: float


def calculate_equivalent_power(
    compressor_power_w: float,
    expander_recovery_w: float,
    refrigeration_load_w: float,
    cold_temperature_k: float,
    ambient_temperature_k: float = 300.0,
) -> EquivalentPowerResult:
    """Compute a simplified equivalent power metric.

    The fallback formulation estimates the equivalent ambient power required
    to sustain refrigeration at low temperature.
    """

    if cold_temperature_k <= 0:
        raise ValueError("cold_temperature_k must be positive")
    if ambient_temperature_k <= cold_temperature_k:
        raise ValueError("ambient_temperature_k must exceed cold temperature")

    carnot_factor = ambient_temperature_k / cold_temperature_k - 1.0

    equivalent = (
        compressor_power_w
        - expander_recovery_w
        + refrigeration_load_w * carnot_factor
    )

    return EquivalentPowerResult(
        compressor_power_w=compressor_power_w,
        expander_recovery_w=expander_recovery_w,
        refrigeration_load_w=refrigeration_load_w,
        carnot_factor=carnot_factor,
        equivalent_power_w=equivalent,
    )
