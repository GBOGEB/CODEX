from gistau_ch15.calculations.expander_replay import CryogenicExpanderReplay
from gistau_ch15.properties.fallback_helium import FallbackHeliumBackend
from gistau_ch15.properties.saturation_overlays import SaturationOverlayBuilder
from gistau_ch15.properties.validation_dataset import (
    CANONICAL_2K_POINTS,
    REFPROP_GAS_REGION_POINTS,
)



def test_canonical_2k_dataset_present():
    assert CANONICAL_2K_POINTS
    assert any(p.temperature_k <= 2.17 for p in CANONICAL_2K_POINTS)



def test_refprop_validation_dataset_present():
    assert REFPROP_GAS_REGION_POINTS
    assert any(p.pressure_kpa > 100.0 for p in REFPROP_GAS_REGION_POINTS)



def test_fallback_saturation_overlay_generation():
    backend = FallbackHeliumBackend()
    builder = SaturationOverlayBuilder()

    rows = builder.build_temperature_trace(
        backend_name="fallback",
        backend=backend,
        fluid="Helium",
        temperatures_k=builder.default_helium_2k_grid(),
    )

    assert rows
    assert any(r.status == "ok" for r in rows)



def test_cryogenic_expander_replay_basic_physics():
    backend = FallbackHeliumBackend()
    replay = CryogenicExpanderReplay()

    result = replay.replay(
        backend=backend,
        fluid="Helium",
        p1_kpa=120.0,
        t1_k=5.0,
        p2_kpa=20.0,
        eta_isentropic=0.75,
        mdot_kg_s=0.05,
    )

    assert result.outlet_pressure_kpa < result.inlet_pressure_kpa
    assert result.outlet_temperature_k <= result.inlet_temperature_k
    assert result.shaft_recovery_w >= 0.0



def test_two_phase_grid_contains_lambda_region_anchor():
    grid = SaturationOverlayBuilder.default_helium_2k_grid()
    assert any(abs(v - 2.17) < 1e-9 for v in grid)
