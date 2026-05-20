from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Iterable

from .base import PropertyBackend


@dataclass(frozen=True)
class SaturationOverlayPoint:
    backend_name: str
    fluid: str
    temperature_k: float
    pressure_kpa: float | None
    liquid_density_kg_m3: float | None
    vapor_density_kg_m3: float | None
    status: str
    notes: str = ""


class SaturationOverlayBuilder:
    """Build saturation dome traces and rho-v overlay rows.

    This is a data layer for docs/gistau-ch15/backend_delta_heatmap.html and
    future publication figures. It deliberately records backend failures per
    point so REFPROP/HEPAK absence or invalid regions become visible data.
    """

    def build_temperature_trace(
        self,
        backend_name: str,
        backend: PropertyBackend,
        fluid: str,
        temperatures_k: Iterable[float],
    ) -> list[SaturationOverlayPoint]:
        rows: list[SaturationOverlayPoint] = []
        for temperature_k in temperatures_k:
            try:
                sat = backend.saturation_t(fluid, temperature_k)
                rows.append(
                    SaturationOverlayPoint(
                        backend_name=backend_name,
                        fluid=fluid,
                        temperature_k=sat.temperature_k,
                        pressure_kpa=sat.pressure_kpa,
                        liquid_density_kg_m3=sat.liquid_density_kg_m3,
                        vapor_density_kg_m3=sat.vapor_density_kg_m3,
                        status="ok",
                    )
                )
            except Exception as exc:
                rows.append(
                    SaturationOverlayPoint(
                        backend_name=backend_name,
                        fluid=fluid,
                        temperature_k=temperature_k,
                        pressure_kpa=None,
                        liquid_density_kg_m3=None,
                        vapor_density_kg_m3=None,
                        status="unavailable_or_invalid",
                        notes=str(exc),
                    )
                )
        return rows

    @staticmethod
    def as_rows(points: Iterable[SaturationOverlayPoint]) -> list[dict[str, Any]]:
        return [asdict(point) for point in points]

    @staticmethod
    def default_helium_2k_grid() -> list[float]:
        return [1.8, 2.0, 2.17, 2.5, 3.0, 4.2, 5.0]
