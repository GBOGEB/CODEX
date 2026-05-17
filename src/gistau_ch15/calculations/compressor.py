from __future__ import annotations

from dataclasses import dataclass
from math import log

from gistau_ch15.properties.base import PropertyBackend

KPA_TO_PA = 1000.0
ISENTROPIC_TEMPERATURE_EXPONENT = 0.28


@dataclass
class CompressorResult:
    inlet_pressure_kpa: float
    outlet_pressure_kpa: float
    inlet_temperature_k: float
    outlet_temperature_k: float
    shaft_power_w: float
    isentropic_shaft_power_w: float | None
    isothermal_efficiency: float
    isentropic_efficiency: float | None


def calculate_compressor(
    backend: PropertyBackend,
    fluid: str,
    p1_kpa: float,
    t1_k: float,
    p2_kpa: float,
    mdot_kg_s: float,
    eta_isothermal: float = 0.5,
    eta_isentropic: float | None = 0.5,
) -> CompressorResult:
    """Fallback compressor calculation.

    This implementation intentionally remains simple until
    REFPROP/HEPAK integration is available.
    """

    if p1_kpa <= 0.0:
        raise ValueError("p1_kpa must be positive")
    if p2_kpa <= p1_kpa:
        raise ValueError("p2_kpa must be greater than p1_kpa")
    if t1_k <= 0.0:
        raise ValueError("t1_k must be positive")
    if mdot_kg_s <= 0.0:
        raise ValueError("mdot_kg_s must be positive")
    if not (0.0 < eta_isothermal <= 1.0):
        raise ValueError("eta_isothermal must satisfy 0 < eta_isothermal <= 1")
    if eta_isentropic is not None and not (0.0 < eta_isentropic <= 1.0):
        raise ValueError("eta_isentropic must satisfy 0 < eta_isentropic <= 1")

    st1 = backend.state_pt(fluid, p1_kpa, t1_k)

    pressure_ratio = p2_kpa / p1_kpa
    t2_k = t1_k * pressure_ratio**ISENTROPIC_TEMPERATURE_EXPONENT

    st2 = backend.state_pt(fluid, p2_kpa, t2_k)

    denominator = st1.density_kg_m3 * st1.temperature_k
    if denominator <= 0.0:
        raise ValueError("backend returned non-physical inlet state for gas constant calculation")

    gas_constant = (st1.pressure_kpa * KPA_TO_PA) / denominator
    isothermal_specific_work_j_kg = gas_constant * t1_k * log(pressure_ratio)
    power = mdot_kg_s * isothermal_specific_work_j_kg / eta_isothermal
    isentropic_power = None

    if eta_isentropic is not None:
        dh = st2.enthalpy_j_kg - st1.enthalpy_j_kg
        if dh <= 0.0:
            raise ValueError("backend returned non-physical enthalpy rise for compressor")
        isentropic_power = mdot_kg_s * dh / eta_isentropic

    return CompressorResult(
        inlet_pressure_kpa=p1_kpa,
        outlet_pressure_kpa=p2_kpa,
        inlet_temperature_k=t1_k,
        outlet_temperature_k=t2_k,
        shaft_power_w=power,
        isentropic_shaft_power_w=isentropic_power,
        isothermal_efficiency=eta_isothermal,
        isentropic_efficiency=eta_isentropic,
    )
