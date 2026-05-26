from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SaturationStubState:
    """Placeholder saturation state used before real two-phase kernels."""

    temperature_k: float
    pressure_kpa: float
    quality: float | None
    validation_status: str
    approximation_note: str


def saturation_state_stub(temperature_k: float, pressure_kpa: float) -> SaturationStubState:
    """Return explicit placeholder saturation information.

    This function intentionally does not solve two-phase helium physics.
    It exists to keep validation paths deterministic until HEPAK/REFPROP/CoolProp
    backend comparisons are wired in.
    """

    return SaturationStubState(
        temperature_k=temperature_k,
        pressure_kpa=pressure_kpa,
        quality=None,
        validation_status="reference_only",
        approximation_note="saturation equation kernel pending; placeholder only",
    )
