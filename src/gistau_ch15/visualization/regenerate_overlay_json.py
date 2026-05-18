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


def regenerate() -> Path:
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
        "saturation": saturation.__dict__,
        "ts_paths": [path.__dict__ for path in ts_paths],
        "phase_map": phase_map.__dict__,
        "expander": [point.__dict__ for point in expander],
        "agreement": agreement.__dict__,
        "backend_delta": deltas.__dict__,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return OUTPUT


if __name__ == "__main__":
    regenerate()
