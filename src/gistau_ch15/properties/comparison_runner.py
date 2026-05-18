from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from gistau_ch15.properties.backend_selector import select_available_backends
from gistau_ch15.properties.compare import (
    BackendDefinition,
    BackendTier,
    StatePointRequest,
    as_report_rows,
    compare_to_reference,
    evaluate_state_points,
)


DEFAULT_REPORT_PATH = Path("docs/gistau-ch15/data/backend_comparison_report.json")


def _tier_for_backend(name: str) -> BackendTier:
    mapping = {
        "fallback": BackendTier.FALLBACK,
        "coolprop": BackendTier.COOLPROP,
        "refprop": BackendTier.REFPROP,
        "hepak": BackendTier.HEPAK,
    }
    return mapping[name]


def build_backend_definitions() -> list[BackendDefinition]:
    backends, _ = select_available_backends()
    definitions: list[BackendDefinition] = []

    for name in ["fallback", "coolprop", "refprop", "hepak"]:
        definitions.append(
            BackendDefinition(
                name=name,
                tier=_tier_for_backend(name),
                backend=backends.get(name),
                role="runtime_validation",
                notes="auto-generated backend definition",
            )
        )

    return definitions


def run_backend_comparison(
    requests: Iterable[StatePointRequest],
    reference_backend: str = "fallback",
    output_path: str | Path = DEFAULT_REPORT_PATH,
):
    definitions = build_backend_definitions()
    results = evaluate_state_points(definitions, requests)
    deltas = compare_to_reference(results, reference_backend)
    rows = as_report_rows(deltas)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")

    return rows
