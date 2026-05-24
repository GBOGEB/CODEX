import pytest

import physics.helium_refrigeration_core as helium_core


def test_compute_g8_exergy_efficiency_delegates_to_shared_kernel(monkeypatch) -> None:
    call_args = {}

    def fake_specific_flow_exergy(**kwargs):
        call_args.update(kwargs)
        return 2.0

    monkeypatch.setattr(helium_core, "specific_flow_exergy", fake_specific_flow_exergy)
    engine = helium_core.CryogenicHeliumEngineG8(t0_ambient=300.0)

    efficiency = engine.compute_g8_exergy_efficiency(
        mass_flow_he=10.0,
        h_in=15.0,
        h_out=32.0,
        s_in=0.03,
        s_out=0.06,
        power_input_kw=100.0,
        nitrogen_assist=False,
    )

    assert efficiency == 0.2
    assert call_args == {
        "h_j_kg": 32.0,
        "s_j_kgk": 0.06,
        "h0_j_kg": 15.0,
        "s0_j_kgk": 0.03,
        "t0_k": 300.0,
    }


def test_compute_g8_exergy_efficiency_nitrogen_toggle_and_zero_power(monkeypatch) -> None:
    monkeypatch.setattr(helium_core, "specific_flow_exergy", lambda **kwargs: 5.0)
    engine = helium_core.CryogenicHeliumEngineG8(nitrogen_assist_gain=1.10)

    with_assist = engine.compute_g8_exergy_efficiency(10.0, 1, 2, 3, 4, 100.0, nitrogen_assist=True)
    without_assist = engine.compute_g8_exergy_efficiency(10.0, 1, 2, 3, 4, 100.0, nitrogen_assist=False)
    zero_power = engine.compute_g8_exergy_efficiency(10.0, 1, 2, 3, 4, 0.0)

    assert with_assist == 0.55
    assert without_assist == 0.5
    assert zero_power == 0.0


def test_compute_g8_exergy_efficiency_clamps_to_unit_interval(monkeypatch) -> None:
    monkeypatch.setattr(helium_core, "specific_flow_exergy", lambda **kwargs: 100.0)
    engine = helium_core.CryogenicHeliumEngineG8()

    assert engine.compute_g8_exergy_efficiency(10.0, 1, 2, 3, 4, 10.0) == 1.0


def test_calculate_g8_covariance_correlation_and_alias() -> None:
    engine = helium_core.CryogenicHeliumEngineG8()
    covariance, correlation = engine.calculate_g8_covariance_correlation([1, 2, 3], [1, 2, 4])
    old_covariance, old_correlation = engine.calculate_g8_anova([1, 2, 3], [1, 2, 4])

    assert covariance == pytest.approx(1.5)
    assert correlation == pytest.approx(0.9819805, rel=1e-6)
    assert old_covariance == covariance
    assert old_correlation == correlation


def test_calculate_g8_covariance_correlation_edge_cases() -> None:
    engine = helium_core.CryogenicHeliumEngineG8()

    assert engine.calculate_g8_covariance_correlation([1], [1]) == (0.0, 0.0)
    assert engine.calculate_g8_covariance_correlation([1, 2], [1]) == (0.0, 0.0)

    covariance, correlation = engine.calculate_g8_covariance_correlation([1, 2, 3], [5, 5, 5])
    assert covariance == 0.0
    assert correlation == 0.0
