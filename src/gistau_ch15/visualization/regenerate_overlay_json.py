from __future__ import annotations

import json
from pathlib import Path

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


OUTPUT = Path("docs/gistau-ch15/data/thermo_visual_overlay_seed.json")


def regenerate(output_path: str | Path = OUTPUT) -> Path:
    """Regenerate overlay JSON with deterministic fallback data.
    
    Args:
        output_path: Path where the overlay JSON will be written.
    """
    saturation = FallbackSaturationSampler().sample()
    ts_paths = FallbackTSReconstructor().build_paths()
    phase_map = FallbackPhaseMapSampler().sample()
    expander = FallbackExpanderValidation().build()
    agreement = BackendAgreementBuilder().build()
    deltas = FallbackBackendDeltaBuilder().build()

    payload = {
        "metadata": {
            "generator": "regenerate_overlay_json",
            "mode": "deterministic_fallback",
        },
        "saturation_dome": {
            "entropy_liquid": saturation.entropy_liquid,
            "temperature_liquid": saturation.temperature_liquid,
            "entropy_vapor": saturation.entropy_vapor,
            "temperature_vapor": saturation.temperature_vapor,
        },
        "ts_paths": [
            {
                "name": path.name,
                "entropy": path.entropy,
                "temperature": path.temperature,
            }
            for path in ts_paths
        ],
        "phase_map": {
            "pressure": phase_map.pressure_kpa,
            "temperature": phase_map.temperature_k,
            "code": phase_map.region_code,
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
        "backend_delta": {
            "backend": deltas.backends,
            "enthalpy_pct": deltas.enthalpy_delta_pct,
            "density_pct": deltas.density_delta_pct,
            "temperature_k": deltas.temperature_delta_k,
        },
    }

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return path


if __name__ == "__main__":
    regenerate()
