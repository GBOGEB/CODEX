from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Optional


@dataclass
class State:
    pressure_kpa: float
    temperature_k: float
    enthalpy_j_kg: float
    entropy_j_kgk: float
    density_kg_m3: float
    quality: Optional[float] = None


@dataclass
class SaturationState:
    pressure_kpa: float
    temperature_k: float
    liquid_density_kg_m3: float
    vapor_density_kg_m3: float


class PropertyBackend(Protocol):
    def state_pt(self, fluid: str, p_kpa: float, t_k: float) -> State: ...
    def state_ph(self, fluid: str, p_kpa: float, h_j_kg: float) -> State: ...
    def state_ps(self, fluid: str, p_kpa: float, s_j_kgk: float) -> State: ...
    def saturation_t(self, fluid: str, t_k: float) -> SaturationState: ...
    def saturation_p(self, fluid: str, p_kpa: float) -> SaturationState: ...
    def quality_ph(self, fluid: str, p_kpa: float, h_j_kg: float) -> Optional[float]: ...
