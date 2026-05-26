from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gistau_ch15.calculations.compressor import calculate_compressor
from gistau_ch15.calculations.expander import calculate_expander
from gistau_ch15.calculations.jt_valve import calculate_jt_valve

DEFAULT_WORKED_EXAMPLES = Path("docs/gistau-ch15/data/worked_examples.json")
REFERENCE_TIER = "tier4_nist_reference"

SUPPORTED_EXAMPLE_IDS = {
    "WE-T00-REFPROP-H-PT-001",
    "WE-T00-REFPROP-HSD-PT-002",
    "WE-T02-FREE-EXPANSION-HEAT-001",
    "WE-T02-SAT-LIQUID-HELIUM-003",
    "WE-T04-CRYOGENIC-EXPANDER-001",
    "WE-T05-CRYOGENIC-COMPRESSOR-001",
}

UNITS_BY_QUANTITY = {
    "enthalpy_j_g": "J/g",
    "entropy_j_gk": "J/g-K",
    "density_kg_m3": "kg/m3",
    "outlet_temperature_k": "K",
    "inlet_enthalpy_j_g": "J/g",
    "outlet_enthalpy_j_g": "J/g",
    "power_w": "W",
    "quality": "fraction",
}

TOLERANCES = {
    "enthalpy_j_g": {"abs": 5.0, "rel": 0.05},
    "entropy_j_gk": {"abs": 5.0, "rel": 0.15},
    "density_kg_m3": {"abs": 0.2, "rel": 0.20},
    "outlet_temperature_k": {"abs": 1.0, "rel": 0.08},
    "inlet_enthalpy_j_g": {"abs": 5.0, "rel": 0.10},
    "outlet_enthalpy_j_g": {"abs": 5.0, "rel": 0.10},
    "power_w": {"abs": 500.0, "rel": 0.20},
    "quality": {"abs": 0.08, "rel": 0.20},
}


class WorkedExampleRunner:
    def __init__(self, worked_examples_path: Path = DEFAULT_WORKED_EXAMPLES) -> None:
        self.worked_examples_path = worked_examples_path

    def load_worked_examples(self) -> list[dict[str, Any]]:
        payload = json.loads(self.worked_examples_path.read_text(encoding="utf-8"))
        return payload.get("examples", [])

    def run_for_backend(
        self,
        backend_name: str,
        backend_tier: str,
        backend: Any | None,
        backend_available: bool,
        unavailable_reason: str = "",
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for example in self.load_worked_examples():
            rows.extend(
                self._run_single_example(
                    example=example,
                    backend_name=backend_name,
                    backend_tier=backend_tier,
                    backend=backend,
                    backend_available=backend_available,
                    unavailable_reason=unavailable_reason,
                )
            )
        return rows

    def _run_single_example(
        self,
        example: dict[str, Any],
        backend_name: str,
        backend_tier: str,
        backend: Any | None,
        backend_available: bool,
        unavailable_reason: str,
    ) -> list[dict[str, Any]]:
        example_id = example["example_id"]
        tuple_id = example["tuple_id"]
        expected_outputs = example.get("expected_outputs", {})
        mapped_quantities = list(expected_outputs.keys()) if example_id in SUPPORTED_EXAMPLE_IDS else []

        if not mapped_quantities:
            return [
                self._row(
                    example_id=example_id,
                    tuple_id=tuple_id,
                    backend_name=backend_name,
                    backend_tier=backend_tier,
                    quantity="mapping",
                    backend_value=None,
                    reference_value=None,
                    unit="",
                    status="mapping_pending",
                    notes="example mapping is not yet implemented in PR-G",
                )
            ]

        if not backend_available or backend is None:
            return [
                self._row(
                    example_id=example_id,
                    tuple_id=tuple_id,
                    backend_name=backend_name,
                    backend_tier=backend_tier,
                    quantity=quantity,
                    backend_value=None,
                    reference_value=expected_outputs.get(quantity),
                    unit=UNITS_BY_QUANTITY.get(quantity, ""),
                    status="backend_unavailable",
                    notes=unavailable_reason or "optional backend unavailable",
                )
                for quantity in mapped_quantities
            ]

        try:
            backend_values, notes = self._execute_mapped_example(example, backend)
        except Exception as exc:
            return [
                self._row(
                    example_id=example_id,
                    tuple_id=tuple_id,
                    backend_name=backend_name,
                    backend_tier=backend_tier,
                    quantity=quantity,
                    backend_value=None,
                    reference_value=expected_outputs.get(quantity),
                    unit=UNITS_BY_QUANTITY.get(quantity, ""),
                    status="not_applicable",
                    notes=f"backend execution failed: {exc}",
                )
                for quantity in mapped_quantities
            ]

        rows: list[dict[str, Any]] = []
        for quantity in mapped_quantities:
            backend_value = backend_values.get(quantity)
            reference_value = expected_outputs.get(quantity)
            status = self._status(quantity, backend_value, reference_value)
            rows.append(
                self._row(
                    example_id=example_id,
                    tuple_id=tuple_id,
                    backend_name=backend_name,
                    backend_tier=backend_tier,
                    quantity=quantity,
                    backend_value=backend_value,
                    reference_value=reference_value,
                    unit=UNITS_BY_QUANTITY.get(quantity, ""),
                    status=status,
                    notes=notes,
                )
            )

        return rows

    @staticmethod
    def _row(
        example_id: str,
        tuple_id: str,
        backend_name: str,
        backend_tier: str,
        quantity: str,
        backend_value: float | None,
        reference_value: float | None,
        unit: str,
        status: str,
        notes: str,
    ) -> dict[str, Any]:
        absolute_delta = None
        relative_delta = None
        if backend_value is not None and reference_value is not None:
            absolute_delta = backend_value - reference_value
            relative_delta = None if reference_value == 0 else absolute_delta / reference_value
        return {
            "example_id": example_id,
            "tuple_id": tuple_id,
            "backend_name": backend_name,
            "backend_tier": backend_tier,
            "reference_tier": REFERENCE_TIER,
            "quantity": quantity,
            "backend_value": backend_value,
            "reference_value": reference_value,
            "absolute_delta": absolute_delta,
            "relative_delta": relative_delta,
            "unit": unit,
            "status": status,
            "notes": notes,
        }

    def _status(self, quantity: str, backend_value: float | None, reference_value: float | None) -> str:
        if reference_value is None:
            return "reference_unavailable"
        if backend_value is None:
            return "not_applicable"
        tolerance = TOLERANCES.get(quantity)
        if tolerance is None:
            return "ok"

        absolute_delta = abs(backend_value - reference_value)
        relative_delta = 0.0 if reference_value == 0 else abs(absolute_delta / reference_value)
        if absolute_delta <= tolerance["abs"] or relative_delta <= tolerance["rel"]:
            return "within_tolerance"
        return "outside_tolerance"

    @staticmethod
    def _execute_mapped_example(example: dict[str, Any], backend: Any) -> tuple[dict[str, float | None], str]:
        example_id = example["example_id"]
        inputs = example.get("inputs", {})
        fluid = str(inputs.get("fluid", "helium"))

        if example_id == "WE-T00-REFPROP-H-PT-001":
            st = backend.state_pt(fluid, inputs["pressure_bar"] * 100.0, inputs["temperature_k"])
            return {"enthalpy_j_g": st.enthalpy_j_kg / 1000.0}, "state_pt(P,T) mapping"

        if example_id == "WE-T00-REFPROP-HSD-PT-002":
            st = backend.state_pt(fluid, inputs["pressure_bar"] * 100.0, inputs["temperature_k"])
            return {
                "enthalpy_j_g": st.enthalpy_j_kg / 1000.0,
                "entropy_j_gk": st.entropy_j_kgk / 1000.0,
                "density_kg_m3": st.density_kg_m3,
            }, "state_pt(P,T) mapping"

        if example_id == "WE-T02-FREE-EXPANSION-HEAT-001":
            jt = calculate_jt_valve(
                backend=backend,
                fluid=fluid,
                p1_kpa=inputs["inlet_pressure_bar"] * 100.0,
                t1_k=inputs["inlet_temperature_k"],
                p2_kpa=inputs["outlet_pressure_bar"] * 100.0,
                mdot_kg_s=inputs["mass_flow_g_s"] / 1000.0,
                heat_leak_w=inputs["thermal_power_w"],
            )
            return {
                "outlet_temperature_k": jt.outlet_temperature_k,
                "inlet_enthalpy_j_g": jt.inlet_enthalpy_j_kg / 1000.0,
                "outlet_enthalpy_j_g": jt.outlet_enthalpy_j_kg / 1000.0,
            }, "calculate_jt_valve mapping"

        if example_id == "WE-T02-SAT-LIQUID-HELIUM-003":
            inlet = backend.state_pt(fluid, inputs["inlet_pressure_bar"] * 100.0, inputs["inlet_temperature_k"])
            outlet = backend.state_ph(fluid, inputs["outlet_pressure_bar"] * 100.0, inlet.enthalpy_j_kg)
            quality = backend.quality_ph(fluid, inputs["outlet_pressure_bar"] * 100.0, inlet.enthalpy_j_kg)
            return {
                "outlet_temperature_k": outlet.temperature_k,
                "quality": quality,
                "enthalpy_j_g": outlet.enthalpy_j_kg / 1000.0,
            }, "saturated liquid expansion via PH mapping"

        if example_id == "WE-T04-CRYOGENIC-EXPANDER-001":
            result = calculate_expander(
                backend=backend,
                fluid=fluid,
                p1_kpa=inputs["inlet_pressure_bar"] * 100.0,
                t1_k=inputs["inlet_temperature_k"],
                p2_kpa=inputs["outlet_pressure_bar"] * 100.0,
                mdot_kg_s=inputs["mass_flow_g_s"] / 1000.0,
                eta_isentropic=inputs["isentropic_efficiency"],
            )
            outlet = backend.state_pt(fluid, result.outlet_pressure_kpa, result.outlet_temperature_k)
            return {
                "outlet_temperature_k": result.outlet_temperature_k,
                "outlet_enthalpy_j_g": outlet.enthalpy_j_kg / 1000.0,
                "power_w": -result.power_output_w,
            }, "calculate_expander mapping"

        if example_id == "WE-T05-CRYOGENIC-COMPRESSOR-001":
            result = calculate_compressor(
                backend=backend,
                fluid=fluid,
                p1_kpa=inputs["inlet_pressure_bar"] * 100.0,
                t1_k=inputs["inlet_temperature_k"],
                p2_kpa=inputs["outlet_pressure_bar"] * 100.0,
                mdot_kg_s=inputs["mass_flow_g_s"] / 1000.0,
                eta_isentropic=inputs["isentropic_efficiency"],
            )
            outlet = backend.state_pt(fluid, result.outlet_pressure_kpa, result.outlet_temperature_k)
            return {
                "outlet_temperature_k": result.outlet_temperature_k,
                "outlet_enthalpy_j_g": outlet.enthalpy_j_kg / 1000.0,
                "power_w": result.shaft_power_w,
            }, "calculate_compressor mapping"

        return {}, "mapping_pending"
