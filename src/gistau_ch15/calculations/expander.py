from __future__ import annotations

from dataclasses import dataclass

from gistau_ch15.properties.base import PropertyBackend

HELIUM_ISENTROPIC_TEMPERATURE_EXPONENT = 0.4
DIATOMIC_ISENTROPIC_TEMPERATURE_EXPONENT = 0.28
DIATOMIC_FLUID_NAMES = {'nitrogen', 'n2', 'ln2', 'liquid nitrogen', 'hydrogen', 'h2'}


@dataclass(frozen=True)
class ExpanderResult:
    inlet_pressure_kpa: float
    outlet_pressure_kpa: float
    inlet_temperature_k: float
    outlet_temperature_k: float
    power_output_w: float
    isentropic_efficiency: float


def _isentropic_temperature_exponent(fluid: str) -> float:
    normalized_fluid = fluid.strip().lower()
    if normalized_fluid in DIATOMIC_FLUID_NAMES:
        return DIATOMIC_ISENTROPIC_TEMPERATURE_EXPONENT
    return HELIUM_ISENTROPIC_TEMPERATURE_EXPONENT


def calculate_expander(
    backend: PropertyBackend,
    fluid: str,
    p1_kpa: float,
    t1_k: float,
    p2_kpa: float,
    mdot_kg_s: float,
    eta_isentropic: float,
) -> ExpanderResult:
    """Simplified deterministic expander tuple calculation.

    The fallback model uses a reversible temperature drop proxy and applies
    isentropic efficiency. Real backends will later provide exact PS/PH states
    and wetness/quality checks.
    """

    if p2_kpa >= p1_kpa:
        raise ValueError("expander outlet pressure must be below inlet pressure")
    if not 0.0 < eta_isentropic <= 1.0:
        raise ValueError("eta_isentropic must be in (0, 1]")
    if mdot_kg_s <= 0:
        raise ValueError("mdot_kg_s must be positive")

    working_fluid = fluid.strip() if fluid and fluid.strip() else 'helium'

    inlet = backend.state_pt(working_fluid, p1_kpa, t1_k)
    pressure_ratio = max(p2_kpa / max(p1_kpa, 1e-9), 1e-9)
    ideal_t2 = t1_k * pressure_ratio ** _isentropic_temperature_exponent(working_fluid)
    actual_t2 = t1_k - eta_isentropic * max(t1_k - ideal_t2, 0.0)
    outlet = backend.state_pt(working_fluid, p2_kpa, actual_t2)

    power = mdot_kg_s * max(inlet.enthalpy_j_kg - outlet.enthalpy_j_kg, 0.0)

    return ExpanderResult(
        inlet_pressure_kpa=p1_kpa,
        outlet_pressure_kpa=p2_kpa,
        inlet_temperature_k=t1_k,
        outlet_temperature_k=actual_t2,
        power_output_w=power,
        isentropic_efficiency=eta_isentropic,
    )
