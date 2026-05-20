from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from gistau_ch15.properties.base import PropertyBackend


@dataclass(frozen=True)
class CryogenicReplayResult:
    inlet_pressure_kpa: float
    outlet_pressure_kpa: float
    inlet_temperature_k: float
    outlet_temperature_k: float
    inlet_entropy_j_kgk: float
    outlet_entropy_j_kgk: float
    inlet_enthalpy_j_kg: float
    outlet_enthalpy_j_kg: float
    enthalpy_drop_j_kg: float
    shaft_recovery_w: float
    outlet_quality: float | None
    phase_stability: str


class CryogenicExpanderReplay:
    """Replay engine for cryogenic expansion trajectories.

    Execution hierarchy:
    deterministic proxy
        → CoolProp states
        → REFPROP gas-region states
        → HEPAK wetness-aware expansion
    """

    def replay(
        self,
        backend: PropertyBackend,
        fluid: str,
        p1_kpa: float,
        t1_k: float,
        p2_kpa: float,
        eta_isentropic: float,
        mdot_kg_s: float,
    ) -> CryogenicReplayResult:
        inlet = backend.state_pt(fluid, p1_kpa, t1_k)

        try:
            outlet_ideal = backend.state_ps(fluid, p2_kpa, inlet.entropy_j_kgk)
        except Exception:
            outlet_ideal = backend.state_pt(fluid, p2_kpa, t1_k * 0.8)

        target_h = inlet.enthalpy_j_kg - eta_isentropic * (
            inlet.enthalpy_j_kg - outlet_ideal.enthalpy_j_kg
        )

        try:
            outlet = backend.state_ph(fluid, p2_kpa, target_h)
        except Exception:
            outlet = outlet_ideal

        enthalpy_drop = inlet.enthalpy_j_kg - outlet.enthalpy_j_kg
        shaft_recovery = max(enthalpy_drop * mdot_kg_s, 0.0)

        quality = outlet.quality
        if quality is None:
            phase_stability = "single_phase_or_unknown"
        elif 0.0 <= quality <= 1.0:
            phase_stability = "two_phase"
        else:
            phase_stability = "unstable"

        return CryogenicReplayResult(
            inlet_pressure_kpa=p1_kpa,
            outlet_pressure_kpa=p2_kpa,
            inlet_temperature_k=t1_k,
            outlet_temperature_k=outlet.temperature_k,
            inlet_entropy_j_kgk=inlet.entropy_j_kgk,
            outlet_entropy_j_kgk=outlet.entropy_j_kgk,
            inlet_enthalpy_j_kg=inlet.enthalpy_j_kg,
            outlet_enthalpy_j_kg=outlet.enthalpy_j_kg,
            enthalpy_drop_j_kg=enthalpy_drop,
            shaft_recovery_w=shaft_recovery,
            outlet_quality=quality,
            phase_stability=phase_stability,
        )

    @staticmethod
    def as_dict(result: CryogenicReplayResult) -> dict[str, Any]:
        return asdict(result)
