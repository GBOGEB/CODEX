from __future__ import annotations

from dataclasses import dataclass

from gistau_ch15.properties.base import PropertyBackend


@dataclass(frozen=True)
class JTValveResult:
    inlet_pressure_kpa: float
    outlet_pressure_kpa: float
    inlet_temperature_k: float
    outlet_temperature_k: float
    inlet_enthalpy_j_kg: float
    outlet_enthalpy_j_kg: float
    energy_residual_j_kg: float


def calculate_jt_valve(
    backend: PropertyBackend,
    fluid: str,
    p1_kpa: float,
    t1_k: float,
    p2_kpa: float,
    mdot_kg_s: float,
    heat_leak_w: float = 0.0,
) -> JTValveResult:
    """Calculate a deterministic isenthalpic/free-expansion step.

    Under fallback mode, outlet temperature is obtained through the backend's
    PH inverse. Real REFPROP/HEPAK backends will later supply phase and quality.
    """

    if mdot_kg_s <= 0:
        raise ValueError("mdot_kg_s must be positive")
    if p2_kpa >= p1_kpa:
        raise ValueError("JT/free expansion expects outlet pressure below inlet pressure")

    inlet = backend.state_pt(fluid, p1_kpa, t1_k)
    outlet_h = inlet.enthalpy_j_kg + heat_leak_w / mdot_kg_s
    outlet = backend.state_ph(fluid, p2_kpa, outlet_h)
    residual = outlet_h - inlet.enthalpy_j_kg - heat_leak_w / mdot_kg_s

    return JTValveResult(
        inlet_pressure_kpa=p1_kpa,
        outlet_pressure_kpa=p2_kpa,
        inlet_temperature_k=t1_k,
        outlet_temperature_k=outlet.temperature_k,
        inlet_enthalpy_j_kg=inlet.enthalpy_j_kg,
        outlet_enthalpy_j_kg=outlet.enthalpy_j_kg,
        energy_residual_j_kg=residual,
    )
