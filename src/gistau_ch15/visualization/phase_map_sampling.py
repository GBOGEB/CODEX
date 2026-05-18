from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PhaseMap:
    pressure_kpa: list[float]
    temperature_k: list[float]
    region_code: list[int]


class FallbackPhaseMapSampler:
    """Deterministic low-temperature phase map scaffold."""

    def sample(self) -> PhaseMap:
        return PhaseMap(
            pressure_kpa=[5, 10, 20, 50, 100, 200, 500, 1000],
            temperature_k=[1.8, 2.0, 2.5, 3.0, 4.2, 5.0, 8.0, 12.0],
            region_code=[1, 1, 2, 2, 2, 3, 3, 3],
        )
