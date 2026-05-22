from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Iterable

from .base import PropertyBackend, State
from .validation_dataset import ValidationPoint, REFPROP_GAS_REGION_POINTS


@dataclass(frozen=True)
class RefpropVerificationRow:
    example_id: str
    tuple_id: str
    backend_name: str
    pressure_kpa: float
    temperature_k: float
    enthalpy_j_kg: float | None
    entropy_j_kgk: float | None
    density_kg_m3: float | None
    quality: float | None
    gas_region: bool | None
    status: str
    notes: str = ""


class RefpropVerificationRunner:
    """Execute canonical REFPROP gas-region verification rows.

    The runner is backend-agnostic for testing, but is intended to receive
    REFPROPAdapter in real verification environments. It records unavailable
    states explicitly instead of dropping rows.
    """

    UNIT_NOTE = (
        "units: pressure[kPa], enthalpy[J/kg], entropy[J/kg-K], density[kg/m3]"
    )

    def run(
        self,
        backend: PropertyBackend,
        backend_name: str = "REFPROP",
        points: Iterable[ValidationPoint] = REFPROP_GAS_REGION_POINTS,
    ) -> list[RefpropVerificationRow]:
        rows: list[RefpropVerificationRow] = []
        for point in points:
            try:
                state = backend.state_pt(point.fluid, point.pressure_kpa, point.temperature_k)
                rows.append(self._row_from_state(point, backend_name, state))
            except Exception as exc:
                rows.append(
                    RefpropVerificationRow(
                        example_id=point.example_id,
                        tuple_id=point.tuple_id,
                        backend_name=backend_name,
                        pressure_kpa=point.pressure_kpa,
                        temperature_k=point.temperature_k,
                        enthalpy_j_kg=None,
                        entropy_j_kgk=None,
                        density_kg_m3=None,
                        quality=None,
                        gas_region=None,
                        status="backend_unavailable_or_failed",
                        notes=f"{self.UNIT_NOTE}; error={exc}",
                    )
                )
        return rows

    @staticmethod
    def _row_from_state(
        point: ValidationPoint,
        backend_name: str,
        state: State,
    ) -> RefpropVerificationRow:
        gas_region = state.quality is None or state.quality >= 1.0
        gas_region_note = "gas_region=confirmed" if gas_region else "gas_region=outside_target"
        return RefpropVerificationRow(
            example_id=point.example_id,
            tuple_id=point.tuple_id,
            backend_name=backend_name,
            pressure_kpa=state.pressure_kpa,
            temperature_k=state.temperature_k,
            enthalpy_j_kg=state.enthalpy_j_kg,
            entropy_j_kgk=state.entropy_j_kgk,
            density_kg_m3=state.density_kg_m3,
            quality=state.quality,
            gas_region=gas_region,
            status="ok" if gas_region else "non_gas_region",
            notes=f"{point.notes}; {RefpropVerificationRunner.UNIT_NOTE}; {gas_region_note}",
        )

    @staticmethod
    def as_rows(rows: Iterable[RefpropVerificationRow]) -> list[dict[str, Any]]:
        return [asdict(row) for row in rows]
