"""Tests for helium_reference and saturation_curves kernels (Issue #71 - PR-H4)."""

from __future__ import annotations

import math

import pytest

from gistau_ch15.kernels.helium_reference import (
    NIST_SATURATION_ANCHORS,
    P_CRITICAL_KPA,
    R_SPECIFIC_J_KGK,
    T_CRITICAL_K,
    T_LAMBDA_K,
    T_NBP_K,
    ideal_gas_density,
    is_supercritical,
    nist_anchor_at_temperature,
    reduced_pressure,
    reduced_temperature,
    saturation_pressure_approx,
)
from gistau_ch15.kernels.saturation_curves import (
    SaturationPoint,
    build_nist_dome,
    sample_dome,
)


# ── helium_reference tests ────────────────────────────────────────────────────

class TestHeliumConstants:
    def test_critical_temperature_in_range(self):
        assert 5.1 < T_CRITICAL_K < 5.3

    def test_critical_pressure_in_range(self):
        assert 200.0 < P_CRITICAL_KPA < 250.0

    def test_specific_gas_constant_approx(self):
        # R for He-4 should be ~2077 J/(kg·K)
        assert 2050.0 < R_SPECIFIC_J_KGK < 2110.0

    def test_lambda_point_below_nbp(self):
        assert T_LAMBDA_K < T_NBP_K

    def test_nbp_below_critical(self):
        assert T_NBP_K < T_CRITICAL_K

    def test_nist_anchors_non_empty(self):
        assert len(NIST_SATURATION_ANCHORS) >= 3


class TestIdealGasDensity:
    def test_density_positive(self):
        rho = ideal_gas_density(p_kpa=101.325, t_k=300.0)
        assert rho > 0.0

    def test_density_decreases_with_temperature(self):
        rho_cold = ideal_gas_density(p_kpa=100.0, t_k=4.2)
        rho_warm = ideal_gas_density(p_kpa=100.0, t_k=300.0)
        assert rho_cold > rho_warm

    def test_density_increases_with_pressure(self):
        rho_low = ideal_gas_density(p_kpa=50.0, t_k=10.0)
        rho_high = ideal_gas_density(p_kpa=200.0, t_k=10.0)
        assert rho_high > rho_low

    def test_raises_on_zero_temperature(self):
        with pytest.raises(ValueError, match="positive"):
            ideal_gas_density(p_kpa=100.0, t_k=0.0)

    def test_raises_on_negative_pressure(self):
        with pytest.raises(ValueError, match="non-negative"):
            ideal_gas_density(p_kpa=-1.0, t_k=10.0)


class TestReducedProperties:
    def test_reduced_temperature_at_critical(self):
        assert reduced_temperature(T_CRITICAL_K) == pytest.approx(1.0)

    def test_reduced_pressure_at_critical(self):
        assert reduced_pressure(P_CRITICAL_KPA) == pytest.approx(1.0)

    def test_subcritical_reduced_temperature(self):
        assert reduced_temperature(T_NBP_K) < 1.0


class TestIsSupercritical:
    def test_supercritical_state(self):
        assert is_supercritical(p_kpa=300.0, t_k=6.0) is True

    def test_subcritical_state(self):
        assert is_supercritical(p_kpa=100.0, t_k=4.0) is False

    def test_on_critical_is_not_supercritical(self):
        assert is_supercritical(p_kpa=P_CRITICAL_KPA, t_k=T_CRITICAL_K) is False


class TestSaturationPressureApprox:
    def test_nbp_pressure_order_of_magnitude(self):
        p = saturation_pressure_approx(T_NBP_K)
        # Should be in the ~70–140 kPa range
        assert 70.0 < p < 140.0

    def test_pressure_increases_with_temperature(self):
        p_low = saturation_pressure_approx(3.0)
        p_high = saturation_pressure_approx(5.0)
        assert p_high > p_low

    def test_raises_below_lambda(self):
        with pytest.raises(ValueError):
            saturation_pressure_approx(1.0)

    def test_raises_above_critical(self):
        with pytest.raises(ValueError):
            saturation_pressure_approx(6.0)


class TestNistAnchorLookup:
    def test_finds_nbp_anchor(self):
        anchor = nist_anchor_at_temperature(T_NBP_K, tolerance_k=0.1)
        assert anchor is not None
        assert anchor["t_k"] == pytest.approx(T_NBP_K, abs=0.1)

    def test_returns_none_when_far(self):
        anchor = nist_anchor_at_temperature(10.0, tolerance_k=0.5)
        assert anchor is None

    def test_anchor_has_required_keys(self):
        anchor = nist_anchor_at_temperature(4.222, tolerance_k=0.1)
        assert anchor is not None
        for key in (
            "t_k", "p_kpa", "rho_liquid_kg_m3", "rho_vapor_kg_m3",
            "h_liquid_j_kg", "h_vapor_j_kg",
        ):
            assert key in anchor


# ── saturation_curves tests ───────────────────────────────────────────────────

class TestBuildNistDome:
    def test_returns_list_of_saturation_points(self):
        dome = build_nist_dome()
        assert len(dome) >= 3
        assert all(isinstance(p, SaturationPoint) for p in dome)

    def test_temperatures_ascending(self):
        dome = build_nist_dome()
        temps = [p.temperature_k for p in dome]
        assert temps == sorted(temps)

    def test_latent_heat_positive(self):
        dome = build_nist_dome()
        for p in dome[:-1]:  # exclude critical point
            assert p.latent_heat_j_kg >= 0.0

    def test_vapor_entropy_exceeds_liquid(self):
        dome = build_nist_dome()
        for p in dome[:-1]:
            assert p.entropy_vapor_j_kgk >= p.entropy_liquid_j_kgk


class TestSampleDome:
    def test_returns_correct_count(self):
        dome = sample_dome(n_points=10)
        assert len(dome) == 10

    def test_temperatures_span_range(self):
        dome = sample_dome(n_points=5, t_min_k=3.0, t_max_k=5.0)
        assert dome[0].temperature_k == pytest.approx(3.0)
        assert dome[-1].temperature_k == pytest.approx(5.0)

    def test_pressures_positive(self):
        dome = sample_dome(n_points=8)
        assert all(p.pressure_kpa > 0.0 for p in dome)

    def test_raises_on_too_few_points(self):
        with pytest.raises(ValueError, match="n_points"):
            sample_dome(n_points=1)

    def test_raises_on_inverted_range(self):
        with pytest.raises(ValueError, match="t_min_k"):
            sample_dome(t_min_k=5.0, t_max_k=3.0)

    def test_entropy_span_non_negative(self):
        dome = sample_dome(n_points=15)
        for p in dome:
            assert p.entropy_span_j_kgk >= 0.0
