from __future__ import annotations

import pytest

from physics.helium_refrigeration_core import CryogenicHeliumEngineG10


def test_exergy_efficiency_includes_nitrogen_assist() -> None:
    engine = CryogenicHeliumEngineG10(t0_ambient=10.0)
    efficiency = engine.compute_g10_exergy_efficiency(
        mass_flow_he=5.0,
        h_in=100.0,
        h_out=130.0,
        s_in=1.0,
        s_out=2.0,
        power_input_kw=100.0,
    )

    assert efficiency == pytest.approx(1.0)


def test_exergy_efficiency_zero_for_non_positive_power() -> None:
    engine = CryogenicHeliumEngineG10()
    efficiency = engine.compute_g10_exergy_efficiency(
        mass_flow_he=5.0,
        h_in=100.0,
        h_out=130.0,
        s_in=1.0,
        s_out=2.0,
        power_input_kw=0.0,
    )

    assert efficiency == 0.0


def test_anova_covariance_and_correlation_for_perfect_alignment() -> None:
    engine = CryogenicHeliumEngineG10()
    covariance, correlation = engine.calculate_g10_anova([1, 2, 3], [1, 2, 3])

    assert covariance == pytest.approx(1.0)
    assert correlation == pytest.approx(1.0)


def test_anova_handles_mismatched_lengths() -> None:
    engine = CryogenicHeliumEngineG10()
    covariance, correlation = engine.calculate_g10_anova([1, 2], [1, 2, 3])

    assert covariance == 0.0
    assert correlation == 0.0


def test_anova_handles_constant_vectors() -> None:
    engine = CryogenicHeliumEngineG10()
    covariance, correlation = engine.calculate_g10_anova([3, 3, 3], [4, 4, 4])

    assert covariance == 0.0
    assert correlation == 0.0
