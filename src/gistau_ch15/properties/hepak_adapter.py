from __future__ import annotations

import importlib
from typing import Any, Optional

from .base import State, SaturationState
from .errors import PropertyBackendUnavailable


class HEPAKAdapter:
    """Optional HEPAK backend scaffold.

    Intended future scope:
    - helium below 5 K,
    - saturated helium,
    - wetness fraction,
    - lambda-region awareness,
    - VLP return analysis,
    - cold-compressor validation.

    This layer remains optional so repository CI can execute without HEPAK.
    """

    backend_name = "HEPAK"

    def __init__(self, fluid: str = "Helium") -> None:
        self.fluid = fluid
        self._binding = self._load_binding()

    def _load_binding(self) -> Any:
        """Load HEPAK Python bindings from supported module names.

        The loader tries ``hepak`` first, then ``pyhepak`` as a fallback.
        If neither import is available, the adapter remains optional by
        raising PropertyBackendUnavailable.
        """
        for module_name in ("hepak", "pyhepak"):
            try:
                return importlib.import_module(module_name)
            except (ImportError, ModuleNotFoundError):
                continue
        raise PropertyBackendUnavailable(
            "HEPAK bindings are not importable. Install/configure HEPAK runtime to enable low-temperature execution."
        )

    def _unavailable(self, call_name: str):
        raise PropertyBackendUnavailable(
            f"HEPAK unavailable for {call_name}. Configure HEPAK bindings before enabling 2 K validation."
        )

    def state_pt(self, fluid: str, p_kpa: float, t_k: float) -> State:
        self._unavailable("state_pt")

    def state_ph(self, fluid: str, p_kpa: float, h_j_kg: float) -> State:
        self._unavailable("state_ph")

    def state_ps(self, fluid: str, p_kpa: float, s_j_kgk: float) -> State:
        self._unavailable("state_ps")

    def saturation_t(self, fluid: str, t_k: float) -> SaturationState:
        self._unavailable("saturation_t")

    def saturation_p(self, fluid: str, p_kpa: float) -> SaturationState:
        self._unavailable("saturation_p")

    def quality_ph(self, fluid: str, p_kpa: float, h_j_kg: float) -> Optional[float]:
        self._unavailable("quality_ph")

    def validate_two_phase_region(self, state: State) -> dict[str, object]:
        quality = state.quality
        return {
            "backend_name": self.backend_name,
            "quality": quality,
            "two_phase_region": quality is not None and 0.0 <= quality <= 1.0,
            "near_2k_region": state.temperature_k <= 5.0,
        }
