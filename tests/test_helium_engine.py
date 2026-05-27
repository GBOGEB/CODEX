"""Unit tests for CryogenicHeliumEngineG5."""
import pytest

from physics.helium_refrigeration_core import CryogenicHeliumEngineG5


@pytest.fixture
def engine():
    return CryogenicHeliumEngineG5()


class TestComputeG5ExergyEfficiency:
    def test_basic_efficiency_in_unit_range(self, engine):
        eta = engine.compute_g5_exergy_efficiency(
            mass_flow_he=11.5,
            h_in=15.0,
            h_out=32.0,
            s_in=0.03,
            s_out=0.06,
            power_input_kw=210.0,
        )
        assert 0.0 <= eta <= 1.0

    def test_nitrogen_assist_reduces_efficiency(self, engine):
        kwargs = dict(
            mass_flow_he=11.5,
            h_in=15.0,
            h_out=32.0,
            s_in=0.03,
            s_out=0.06,
            power_input_kw=210.0,
        )
        eta_with = engine.compute_g5_exergy_efficiency(**kwargs, nitrogen_assist=True)
        eta_without = engine.compute_g5_exergy_efficiency(**kwargs, nitrogen_assist=False)
        # Nitrogen assist applies a 10% mass-flow reduction, so efficiency should be lower
        assert eta_with < eta_without

    def test_zero_power_input_returns_zero(self, engine):
        eta = engine.compute_g5_exergy_efficiency(
            mass_flow_he=11.5,
            h_in=15.0,
            h_out=32.0,
            s_in=0.03,
            s_out=0.06,
            power_input_kw=0.0,
        )
        assert eta == 0.0

    def test_negative_power_input_returns_zero(self, engine):
        eta = engine.compute_g5_exergy_efficiency(
            mass_flow_he=11.5,
            h_in=15.0,
            h_out=32.0,
            s_in=0.03,
            s_out=0.06,
            power_input_kw=-50.0,
        )
        assert eta == 0.0

    def test_efficiency_clamped_to_one(self, engine):
        # Very high mass flow relative to power clamps at 1.0
        eta = engine.compute_g5_exergy_efficiency(
            mass_flow_he=1e6,
            h_in=0.0,
            h_out=1000.0,
            s_in=0.0,
            s_out=0.0,
            power_input_kw=1.0,
            nitrogen_assist=False,
        )
        assert eta == 1.0


class TestCalculateWaveAnova:
    def test_perfect_correlation(self, engine):
        v = [0.2, 0.4, 0.6, 0.8, 1.0]
        cov, corr = engine.calculate_wave_anova(v, v)
        assert abs(corr - 1.0) < 1e-9

    def test_near_perfect_correlation(self, engine):
        claimed = [0.20, 0.40, 0.60, 0.80, 1.00]
        actual = [0.19, 0.38, 0.58, 0.81, 0.99]
        cov, corr = engine.calculate_wave_anova(claimed, actual)
        assert 0.99 < corr <= 1.0
        assert cov > 0.0

    def test_mismatched_lengths_returns_zero(self, engine):
        cov, corr = engine.calculate_wave_anova([0.1, 0.2], [0.1])
        assert cov == 0.0
        assert corr == 0.0

    def test_single_element_returns_zero(self, engine):
        cov, corr = engine.calculate_wave_anova([0.5], [0.5])
        assert cov == 0.0
        assert corr == 0.0

    def test_empty_vectors_return_zero(self, engine):
        cov, corr = engine.calculate_wave_anova([], [])
        assert cov == 0.0
        assert corr == 0.0

    def test_zero_variance_vector_returns_zero_correlation(self, engine):
        # Constant vector has zero variance; correlation should be 0.0
        cov, corr = engine.calculate_wave_anova([1.0, 1.0, 1.0], [0.1, 0.2, 0.3])
        assert corr == 0.0

    def test_covariance_sign(self, engine):
        # Negatively correlated vectors
        claimed = [0.2, 0.4, 0.6, 0.8]
        actual = [0.8, 0.6, 0.4, 0.2]
        cov, corr = engine.calculate_wave_anova(claimed, actual)
        assert cov < 0.0
        assert corr < 0.0
