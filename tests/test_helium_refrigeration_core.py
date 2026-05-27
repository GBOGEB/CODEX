import pytest

from helium_refrigeration_core import CryogenicHeliumEngineG4


def test_compute_g4_dynamic_exergy_nominal_value() -> None:
    engine = CryogenicHeliumEngineG4()
    result = engine.compute_g4_dynamic_exergy(
        mass_flow=11.5,
        h_in=12.0,
        h_out=28.5,
        s_in=0.04,
        s_out=0.07,
        power_kw=220.0,
    )
    assert result == pytest.approx(0.43444125)


def test_compute_g4_dynamic_exergy_ln2_assist_branch() -> None:
    engine = CryogenicHeliumEngineG4()
    with_assist = engine.compute_g4_dynamic_exergy(
        mass_flow=11.5,
        h_in=12.0,
        h_out=28.5,
        s_in=0.04,
        s_out=0.07,
        power_kw=220.0,
        ln2_assist=True,
    )
    without_assist = engine.compute_g4_dynamic_exergy(
        mass_flow=11.5,
        h_in=12.0,
        h_out=28.5,
        s_in=0.04,
        s_out=0.07,
        power_kw=220.0,
        ln2_assist=False,
    )
    assert with_assist > without_assist
    assert without_assist == pytest.approx(0.39494659090909087)


def test_compute_g4_dynamic_exergy_zero_or_negative_power() -> None:
    engine = CryogenicHeliumEngineG4()
    assert engine.compute_g4_dynamic_exergy(1.0, 10.0, 20.0, 0.01, 0.02, 0.0) == 0.0
    assert engine.compute_g4_dynamic_exergy(1.0, 10.0, 20.0, 0.01, 0.02, -5.0) == 0.0


def test_compute_g4_dynamic_exergy_clamping() -> None:
    engine = CryogenicHeliumEngineG4()
    clamped_high = engine.compute_g4_dynamic_exergy(
        mass_flow=1000.0,
        h_in=12.0,
        h_out=28.5,
        s_in=0.04,
        s_out=0.07,
        power_kw=220.0,
    )
    clamped_low = engine.compute_g4_dynamic_exergy(
        mass_flow=2.0,
        h_in=30.0,
        h_out=10.0,
        s_in=0.00,
        s_out=0.10,
        power_kw=5.0,
    )
    assert clamped_high == 1.0
    assert clamped_low == 0.0


def test_compute_wave_metrics_anova_nominal_values() -> None:
    engine = CryogenicHeliumEngineG4()
    covariance, correlation = engine.compute_wave_metrics_anova(
        [0.25, 0.50, 0.75, 1.00],
        [0.22, 0.49, 0.74, 0.99],
    )
    assert covariance == pytest.approx(0.10666666666666667)
    assert correlation == pytest.approx(0.9998169448073261)


def test_compute_wave_metrics_anova_invalid_and_zero_variance_cases() -> None:
    engine = CryogenicHeliumEngineG4()
    assert engine.compute_wave_metrics_anova([0.1], [0.1]) == (0.0, 0.0)
    assert engine.compute_wave_metrics_anova([0.1, 0.2], [0.1]) == (0.0, 0.0)
    assert engine.compute_wave_metrics_anova([1.0, 1.0], [2.0, 2.0]) == (0.0, 0.0)
