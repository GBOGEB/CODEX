import pytest

from src.g3_engine.helium_refrigeration_core import CryogenicHeliumEngine


def test_compute_exergy_efficiency_clamps_to_one() -> None:
    engine = CryogenicHeliumEngine()
    result = engine.compute_exergy_efficiency(
        mass_flow=100.0,
        enthalpy_in=0.0,
        enthalpy_out=1000.0,
        entropy_in=0.0,
        entropy_out=0.0,
        power_kw=1.0,
    )
    assert result == 1.0


def test_compute_exergy_efficiency_zero_or_negative_power_returns_zero() -> None:
    engine = CryogenicHeliumEngine()
    assert (
        engine.compute_exergy_efficiency(
            mass_flow=1.0,
            enthalpy_in=10.0,
            enthalpy_out=20.0,
            entropy_in=0.1,
            entropy_out=0.2,
            power_kw=0.0,
        )
        == 0.0
    )
    assert (
        engine.compute_exergy_efficiency(
            mass_flow=1.0,
            enthalpy_in=10.0,
            enthalpy_out=20.0,
            entropy_in=0.1,
            entropy_out=0.2,
            power_kw=-5.0,
        )
        == 0.0
    )


def test_compute_exergy_efficiency_clamps_to_zero_when_negative() -> None:
    engine = CryogenicHeliumEngine()
    # Negative delta_h drives useful_exergy_power below zero; result must clamp to 0.0
    result = engine.compute_exergy_efficiency(
        mass_flow=1.0,
        enthalpy_in=100.0,
        enthalpy_out=50.0,
        entropy_in=0.0,
        entropy_out=0.0,
        power_kw=1.0,
    )
    assert result == 0.0


def test_calculate_covariance_returns_zero_on_vector_length_mismatch() -> None:
    engine = CryogenicHeliumEngine()
    assert engine.calculate_covariance([0.2, 0.3], [0.2]) == 0.0


def test_calculate_covariance_matches_expected_sample_covariance() -> None:
    engine = CryogenicHeliumEngine()
    covariance = engine.calculate_covariance([0.2, 0.4, 0.6], [0.1, 0.3, 0.5])
    assert covariance == pytest.approx(0.04)
