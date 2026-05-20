import json

from gistau_ch15.visualization.backend_agreement import (
    BackendAgreementBuilder,
)
from gistau_ch15.visualization.expander_validation import (
    FallbackExpanderValidation,
)
from gistau_ch15.visualization.phase_map_sampling import (
    FallbackPhaseMapSampler,
)
from gistau_ch15.visualization import regenerate_overlay_json
from gistau_ch15.visualization.ts_reconstruction import (
    FallbackTSReconstructor,
)


def test_ts_reconstruction_returns_paths():
    paths = FallbackTSReconstructor().build_paths()

    assert len(paths) >= 1


def test_phase_map_sampler_returns_points():
    phase_map = FallbackPhaseMapSampler().sample()

    assert len(phase_map.pressure_kpa) > 0


def test_expander_validation_returns_points():
    points = FallbackExpanderValidation().build()

    assert len(points) >= 1


def test_backend_agreement_builder_returns_matrix():
    matrix = BackendAgreementBuilder().build()

    assert len(matrix.values) > 0


def test_regenerate_overlay_json_matches_dashboard_schema(tmp_path):
    output = tmp_path / "seed.json"
    regenerate_overlay_json.regenerate(output)

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert "saturation_dome" in payload
    assert payload["phase_map"].keys() == {"pressure", "temperature", "code"}
    assert len(payload["phase_map"]["pressure"]) == len(
        payload["phase_map"]["temperature"]
    )
    assert len(payload["phase_map"]["code"]) == len(
        payload["phase_map"]["temperature"]
    )
    assert all(
        isinstance(value, (int, float))
        for value in payload["phase_map"]["temperature"]
    )
    assert payload["backend_delta"].keys() == {
        "backend",
        "enthalpy_pct",
        "density_pct",
        "temperature_k",
    }
    assert payload["expander"].keys() == {"station", "temperature", "pressure"}
    assert payload["agreement"].keys() == {"x", "y", "z"}
