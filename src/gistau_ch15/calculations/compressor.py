from __future__ import annotations

from dataclasses import dataclass

from gistau_ch15.properties.base import PropertyBackend


@dataclass
class CompressorResult:
    inlet_pressure_kpa: float
    outlet_pressure_kpa: float
    inlet_temperature_k: float
    outlet_temperature_k: float
    shaft_power_w: float
    isothermal_efficiency: float


def calculate_compressor(
    backend: PropertyBackend,
    fluid: str,
    p1_kpa: float,
    t1_k: float,
    p2_kpa: float,
    mdot_kg_s: float,
    eta_isentropic: float,
) -> CompressorResult:
    """Fallback compressor calculation.

    This implementation intentionally remains simple until
    REFPROP/HEPAK integration is available.
    """

    st1 = backend.state_pt(fluid, p1_kpa, t1_k)

    pressure_ratio = max(p2_kpa / max(p1_kpa, 1e-9), 1.0)
    t2_k = t1_k * pressure_ratio ** 0.28

    st2 = backend.state_pt(fluid, p2_kpa, t2_k)

    dh = max(st2.enthalpy_j_kg - st1.enthalpy_j_kg, 0.0)
    power = mdot_kg_s * dh / max(eta_isentropic, 1e-9)

    return CompressorResult(
        inlet_pressure_kpa=p1_kpa,
        outlet_pressure_kpa=p2_kpa,
        inlet_temperature_k=t1_k,
        outlet_temperature_k=t2_k,
        shaft_power_w=power,
        isothermal_efficiency=eta_isentropic,
    )
