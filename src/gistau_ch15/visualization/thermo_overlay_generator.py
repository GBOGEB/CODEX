from __future__ import annotations

import json
from pathlib import Path
from typing import Any


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
        return {
            "metadata": {
                "generator": "ThermoOverlayGenerator",
                "mode": "deterministic_fallback",
                "phase": "PR-H",
            },
            "saturation": {
                "entropy_liquid": [5, 12, 20, 31, 45, 62],
                "temperature_liquid": [1.8, 2.0, 2.4, 3.0, 3.8, 4.6],
                "entropy_vapor": [450, 390, 330, 270, 220, 180],
                "temperature_vapor": [1.8, 2.0, 2.4, 3.0, 3.8, 4.6],
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
