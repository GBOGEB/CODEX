from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gistau_ch15.visualization.backend_agreement import (
    BackendAgreementBuilder,
)
from gistau_ch15.visualization.backend_delta_matrix import (
    FallbackBackendDeltaBuilder,
)
from gistau_ch15.visualization.expander_validation import (
    FallbackExpanderValidation,
)
from gistau_ch15.visualization.phase_map_sampling import (
    FallbackPhaseMapSampler,
)
from gistau_ch15.visualization.saturation_sampling import (
    FallbackSaturationSampler,
)
from gistau_ch15.visualization.ts_reconstruction import (
    FallbackTSReconstructor,
)


DEFAULT_OUTPUT = Path(
    "docs/gistau-ch15/data/thermo_visual_overlay_seed.json"
)


class ThermoOverlayGenerator:
    """Deterministic visualization generator scaffold.

    Parent rules:
    - generated artifacts must remain GitHub Pages visible
    - optional thermodynamic runtimes remain optional
    - fallback generation must always succeed
    - visualization schema stability is prioritized
    - generated files evolve iteratively through PR-Hx branches
    """

    def build_seed_dataset(self) -> dict[str, Any]:
        saturation = FallbackSaturationSampler().sample()
        ts_paths = FallbackTSReconstructor().build_paths()
        phase_map = FallbackPhaseMapSampler().sample()
        expander = FallbackExpanderValidation().build()
        agreement = BackendAgreementBuilder().build()
        deltas = FallbackBackendDeltaBuilder().build()

        return {
            "metadata": {
                "generator": "ThermoOverlayGenerator",
                "mode": "deterministic_fallback",
                "phase": "PR-H",
            },
            "saturation_dome": saturation.__dict__,
            "ts_paths": [path.__dict__ for path in ts_paths],
            "phase_map": {
                "pressure": phase_map.pressure_kpa,
                "temperature": phase_map.temperature_k,
                "code": phase_map.region_code,
            },
            "backend_delta": {
                "backend": deltas.backends,
                "enthalpy_pct": deltas.enthalpy_delta_pct,
                "density_pct": deltas.density_delta_pct,
                "temperature_k": deltas.temperature_delta_k,
            },
            "expander": {
                "station": [point.station for point in expander],
                "temperature": [point.temperature_k for point in expander],
                "pressure": [point.pressure_kpa for point in expander],
            },
            "agreement": {
                "x": agreement.backends,
                "y": agreement.tuples,
                "z": agreement.values,
            },
            "backend_status": {
                "fallback": "available",
                "coolprop": "optional",
                "refprop": "optional",
                "hepak": "optional",
            },
        }

    def write_json(
        self,
        output_path: str | Path = DEFAULT_OUTPUT,
    ) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = self.build_seed_dataset()

        path.write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
        )

        return path


if __name__ == "__main__":
    ThermoOverlayGenerator().write_json()
