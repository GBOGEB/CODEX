from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from gistau_ch15.calculations.compressor import calculate_compressor
from gistau_ch15.calculations.expander import calculate_expander
from gistau_ch15.calculations.jt_valve import calculate_jt_valve
from gistau_ch15.calculations.equivalent_power import calculate_equivalent_power
from gistau_ch15.properties.fallback_helium import FallbackHeliumBackend


@dataclass(frozen=True)
class CalculationRow:
    example_id: str
    tuple_id: str
    calculation: str
    quantity: str
    calculated_value: float | None
    expected_value: float | None
    absolute_delta: float | None
    relative_delta: float | None
    unit: str
    status: str
    notes: str


def _delta(calc: float | None, expected: float | None) -> tuple[float | None, float | None]:
    if calc is None or expected is None:
        return None, None
    absolute = calc - expected
    relative = None if expected == 0 else absolute / expected
    return absolute, relative


def _row(example_id: str, tuple_id: str, calculation: str, quantity: str, calc: float | None, expected: float | None, unit: str, status: str, notes: str) -> CalculationRow:
    absolute, relative = _delta(calc, expected)
    return CalculationRow(
        example_id=example_id,
        tuple_id=tuple_id,
        calculation=calculation,
        quantity=quantity,
        calculated_value=calc,
        expected_value=expected,
        absolute_delta=absolute,
        relative_delta=relative,
        unit=unit,
        status=status,
        notes=notes,
    )


def run_seed_calculations() -> list[CalculationRow]:
    """Run first executable calculation pass for selected GISTAU examples.

    This is intentionally fallback-backend based. It provides executable rows,
    deltas and status flags now, while REFPROP/HEPAK/CoolProp are integrated in
    later passes.
    """

    backend = FallbackHeliumBackend()
    rows: list[CalculationRow] = []

    # T00 property H/S/D at 1 bar and 300 K.
    st = backend.state_pt("helium", 100.0, 300.0)
    rows.append(_row("WE-T00-REFPROP-H-PT-001", "T00", "state_pt", "enthalpy", st.enthalpy_j_kg / 1000.0, 1563.3194, "J/g", "outside_tolerance", "fallback ideal-gas cp estimate; REFPROP expected"))
    rows.append(_row("WE-T00-REFPROP-HSD-PT-002", "T00", "state_pt", "entropy", st.entropy_j_kgk / 1000.0, 28.0075, "J/g-K", "outside_tolerance", "fallback entropy placeholder is not thermodynamic entropy"))
    rows.append(_row("WE-T00-REFPROP-HSD-PT-002", "T00", "state_pt", "density", st.density_kg_m3, 0.1604, "kg/m3", "outside_tolerance", "fallback ideal-gas density estimate"))

    # T02 JT/free expansion example.
    jt = calculate_jt_valve(
        backend=backend,
        fluid="helium",
        p1_kpa=1400.0,
        t1_k=20.0,
        p2_kpa=100.0,
        mdot_kg_s=0.050,
        heat_leak_w=100.0,
    )
    rows.append(_row("WE-T02-FREE-EXPANSION-HEAT-001", "T02", "calculate_jt_valve", "outlet_temperature", jt.outlet_temperature_k, 19.16, "K", "outside_tolerance", "fallback cp model cannot reproduce real JT cooling/heating inversion"))
    rows.append(_row("WE-T02-FREE-EXPANSION-HEAT-001", "T02", "calculate_jt_valve", "outlet_enthalpy", jt.outlet_enthalpy_j_kg / 1000.0, 103.92, "J/g", "within_fallback_logic", "energy balance includes heat input per unit mass"))

    # T04 expander example.
    exp = calculate_expander(
        backend=backend,
        fluid="helium",
        p1_kpa=1400.0,
        t1_k=25.0,
        p2_kpa=120.0,
        mdot_kg_s=0.050,
        eta_isentropic=0.75,
    )
    rows.append(_row("WE-T04-CRYOGENIC-EXPANDER-001", "T04", "calculate_expander", "outlet_temperature", exp.outlet_temperature_k, 12.93, "K", "outside_tolerance", "fallback pressure-ratio proxy; needs REFPROP/HEPAK PS path"))
    rows.append(_row("WE-T04-CRYOGENIC-EXPANDER-001", "T04", "calculate_expander", "power", -exp.power_output_w, -2981.6, "W", "outside_tolerance", "negative sign used to match source convention; numeric needs real backend"))

    # T05 cryogenic compressor approximated with compressor tuple.
    comp = calculate_compressor(
        backend=backend,
        fluid="helium",
        p1_kpa=50.0,
        t1_k=5.0,
        p2_kpa=170.0,
        mdot_kg_s=0.400,
        eta_isentropic=0.75,
    )
    rows.append(_row("WE-T05-CRYOGENIC-COMPRESSOR-001", "T05", "calculate_compressor", "outlet_temperature", comp.outlet_temperature_k, 7.72, "K", "outside_tolerance", "fallback compressor model; HEPAK priority below 5 K"))
    rows.append(_row("WE-T05-CRYOGENIC-COMPRESSOR-001", "T05", "calculate_compressor", "power", comp.shaft_power_w, 5336.0, "W", "outside_tolerance", "cold compressor requires real-fluid backend"))

    # T06 equivalent power rough roll-up.
    eq = calculate_equivalent_power(
        compressor_power_w=3150_000.0,
        expander_recovery_w=0.0,
        refrigeration_load_w=10.0,
        cold_temperature_k=4.5,
        ambient_temperature_k=300.0,
    )
    rows.append(_row("WE-T06-EQUIVALENT-POWER-001", "T06", "calculate_equivalent_power", "equivalent_power", eq.equivalent_power_w, 906643.0, "W", "mapping_pending", "source roll-up requires column mapping and FOM treatment"))

    return rows


def run_seed_calculation_report() -> list[dict[str, Any]]:
    return [asdict(row) for row in run_seed_calculations()]
