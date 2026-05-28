"""Unit tests for CryogenicHeliumEngineG7."""
from helium_refrigeration_core import CryogenicHeliumEngineG7

class TestComputeG7ExergyEfficiency:
    def setup_method(self):
        self.engine = CryogenicHeliumEngineG7()

    def test_typical_inputs_returns_expected_efficiency(self):
        result = self.engine.compute_g7_exergy_efficiency(
            mass_flow_he=11.5,
            h_in=15.0,
            h_out=32.0,
            s_in=0.03,
            s_out=0.06,
            power_input_kw=210.0,
        )
        assert 0.0 < result <= 1.0
        assert abs(result - 0.4852) < 0.001

    def test_zero_power_input_returns_zero(self):
        result = self.engine.compute_g7_exergy_efficiency(
            mass_flow_he=11.5, h_in=15.0, h_out=32.0,
            s_in=0.03, s_out=0.06, power_input_kw=0.0,
        )
        assert result == 0.0

    def test_negative_power_input_returns_zero(self):
        result = self.engine.compute_g7_exergy_efficiency(
            mass_flow_he=11.5, h_in=15.0, h_out=32.0,
            s_in=0.03, s_out=0.06, power_input_kw=-50.0,
        )
        assert result == 0.0

    def test_nitrogen_assist_true_gives_higher_efficiency(self):
        with_assist = self.engine.compute_g7_exergy_efficiency(
            mass_flow_he=11.5, h_in=15.0, h_out=32.0,
            s_in=0.03, s_out=0.06, power_input_kw=210.0,
            nitrogen_assist=True,
        )
        without_assist = self.engine.compute_g7_exergy_efficiency(
            mass_flow_he=11.5, h_in=15.0, h_out=32.0,
            s_in=0.03, s_out=0.06, power_input_kw=210.0,
            nitrogen_assist=False,
        )
        assert without_assist < with_assist

    def test_clamp_upper_bound_at_one(self):
        # Very high mass_flow relative to power should clamp at 1.0
        result = self.engine.compute_g7_exergy_efficiency(
            mass_flow_he=1000.0, h_in=0.0, h_out=100.0,
            s_in=0.0, s_out=0.0, power_input_kw=1.0,
        )
        assert result == 1.0

    def test_clamp_lower_bound_at_zero(self):
        # Negative exergy (h_out < h_in) should clamp at 0.0
        result = self.engine.compute_g7_exergy_efficiency(
            mass_flow_he=11.5, h_in=32.0, h_out=15.0,
            s_in=0.06, s_out=0.03, power_input_kw=210.0,
        )
        assert result == 0.0


class TestCalculatePearsonCorrelation:
    def setup_method(self):
        self.engine = CryogenicHeliumEngineG7()

    def test_identical_vectors_return_correlation_one(self):
        v = [1.0, 2.0, 3.0, 4.0, 5.0]
        _, r = self.engine.calculate_pearson_correlation(v, v)
        assert abs(r - 1.0) < 1e-9

    def test_perfectly_anticorrelated_vectors(self):
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [5.0, 4.0, 3.0, 2.0, 1.0]
        _, r = self.engine.calculate_pearson_correlation(x, y)
        assert abs(r - (-1.0)) < 1e-9

    def test_known_correlation_value(self):
        claimed = [0.20, 0.40, 0.60, 0.80, 1.00]
        actual = [0.20, 0.41, 0.59, 0.80, 1.00]
        _, r = self.engine.calculate_pearson_correlation(claimed, actual)
        assert abs(r - 0.99976) < 0.0001

    def test_constant_vector_zero_variance_returns_zero(self):
        x = [1.0, 1.0, 1.0, 1.0]
        y = [1.0, 2.0, 3.0, 4.0]
        cov, r = self.engine.calculate_pearson_correlation(x, y)
        assert r == 0.0

    def test_mismatched_lengths_returns_zero(self):
        cov, r = self.engine.calculate_pearson_correlation([1, 2, 3], [1, 2])
        assert cov == 0.0
        assert r == 0.0

    def test_single_element_returns_zero(self):
        cov, r = self.engine.calculate_pearson_correlation([1.0], [1.0])
        assert cov == 0.0
        assert r == 0.0

    def test_empty_vectors_returns_zero(self):
        cov, r = self.engine.calculate_pearson_correlation([], [])
        assert cov == 0.0
        assert r == 0.0
