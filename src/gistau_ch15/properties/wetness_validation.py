from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Iterable

from .base import PropertyBackend
from .validation_dataset import CANONICAL_2K_POINTS, ValidationPoint


@dataclass(frozen=True)
class WetnessValidationRow:
    example_id: str
    tuple_id: str
    backend_name: str
    temperature_k: float
    pressure_kpa: float
    quality: float | None
    wetness_fraction: float | None
    phase_region: str
    status: str
    notes: str = ""


class WetnessValidationRunner:
    """Wetness-aware validation near the 2 K helium corridor.

    Intended primary backend:
    HEPAK.

    Fallback/CoolProp/REFPROP executions remain useful for cross-checks,
    unavailable-state reporting and divergence mapping.
    """

    def run(
        self,
        backend: PropertyBackend,
        backend_name: str,
        points: Iterable[ValidationPoint] = CANONICAL_2K_POINTS,
    ) -> list[WetnessValidationRow]:
        rows: list[WetnessValidationRow] = []

        for point in points:
            try:
                state = backend.state_pt(
                    point.fluid,
                    point.pressure_kpa,
                    point.temperature_k,
                )

                quality = state.quality
                lambda_region = state.temperature_k <= 2.17

                if quality is None:
                    wetness_fraction = None
                    phase_region = (
                        "lambda_region_single_phase_or_unknown"
                        if lambda_region
                        else "single_phase_or_unknown"
                    )
                else:
                    bounded_quality = quality if 0.0 <= quality <= 1.0 else None
                    if bounded_quality is None:
                        wetness_fraction = None
                        quality = bounded_quality
                        phase_region = "quality_out_of_range"
                    else:
                        quality = bounded_quality
                        wetness_fraction = 1.0 - quality
                        phase_region = "lambda_region_two_phase" if lambda_region else "two_phase"

                rows.append(
                    WetnessValidationRow(
                        example_id=point.example_id,
                        tuple_id=point.tuple_id,
                        backend_name=backend_name,
                        temperature_k=state.temperature_k,
                        pressure_kpa=state.pressure_kpa,
                        quality=quality,
                        wetness_fraction=wetness_fraction,
                        phase_region=phase_region,
                        status="ok",
                        notes=point.notes,
                    )
                )

            except Exception as exc:
                rows.append(
                    WetnessValidationRow(
                        example_id=point.example_id,
                        tuple_id=point.tuple_id,
                        backend_name=backend_name,
                        temperature_k=point.temperature_k,
                        pressure_kpa=point.pressure_kpa,
                        quality=None,
                        wetness_fraction=None,
                        phase_region="unavailable",
                        status="backend_unavailable_or_failed",
                        notes=str(exc),
                    )
                )

        return rows

    @staticmethod
    def as_rows(rows: Iterable[WetnessValidationRow]) -> list[dict[str, Any]]:
        return [asdict(row) for row in rows]
