from gistau_ch15.visualization.thermo_overlay_generator import (
    ThermoOverlayGenerator,
)


def test_overlay_generator_returns_payload():
    payload = ThermoOverlayGenerator().build_seed_dataset()

    assert "metadata" in payload
    assert "saturation_dome" in payload
    assert "ts_paths" in payload
    assert "phase_map" in payload
    assert "backend_delta" in payload
    assert "expander" in payload
    assert "agreement" in payload
    assert "backend_status" in payload


def test_overlay_generator_has_fallback_backend():
    payload = ThermoOverlayGenerator().build_seed_dataset()

    assert payload["backend_status"]["fallback"] == "available"
