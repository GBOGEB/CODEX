from gistau_ch15.visualization.thermo_overlay_generator import (
    ThermoOverlayGenerator,
)


def test_overlay_generator_returns_payload():
    payload = ThermoOverlayGenerator().build_seed_dataset()

    assert "metadata" in payload
    assert "saturation" in payload
    assert "backend_status" in payload


def test_overlay_generator_has_fallback_backend():
    payload = ThermoOverlayGenerator().build_seed_dataset()

    assert payload["backend_status"]["fallback"] == "available"
