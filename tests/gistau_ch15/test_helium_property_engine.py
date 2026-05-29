"""Tests for HeliumPropertyEngine and verify_mass_balance (P2-3 buildout)."""

from __future__ import annotations

import pytest

from src.gistau_ch15.properties.helium_property_engine import (
    HeliumPropertyEngine,
    verify_mass_balance,
)
from src.gistau_ch15.kernels.helium_reference import T_LAMBDA_K


class TestHeliumPropertyEngine:
    def test_enthalpy_above_lambda_is_finite(self):
        engine = HeliumPropertyEngine()
        h = engine.get_enthalpy(4.2)
        assert isinstance(h, float)
        assert -1000.0 < h < 10000.0

    def test_enthalpy_below_lambda_uses_power_law(self):
        engine = HeliumPropertyEngine()
        h_below = engine.get_enthalpy(T_LAMBDA_K - 0.1)
        # Power law: 4.22 * T^5.6; at ~2.07 K should be positive and small
        assert h_below > 0.0

    def test_enthalpy_increases_with_temperature(self):
        engine = HeliumPropertyEngine()
        h1 = engine.get_enthalpy(4.0)
        h2 = engine.get_enthalpy(5.0)
        assert h2 > h1

    def test_enthalpy_accepts_pressure_arg(self):
        """Pressure argument accepted without error (interface compatibility)."""
        engine = HeliumPropertyEngine()
        h = engine.get_enthalpy(4.5, pressure_bar=1.2)
        assert isinstance(h, float)

    def test_raises_on_zero_temperature(self):
        engine = HeliumPropertyEngine()
        with pytest.raises(ValueError, match="positive"):
            engine.get_enthalpy(0.0)

    def test_custom_coefficients(self):
        engine = HeliumPropertyEngine(poly_coeffs=(-2.0, 6.0, 13.0))
        h = engine.get_enthalpy(4.2)
        expected = -2.0 + 6.0 * 4.2 + 13.0 * (4.2 ** 2)
        assert abs(h - expected) < 1e-9


class TestVerifyMassBalance:
    def test_returns_expected_keys(self):
        result = verify_mass_balance(16.0)
        assert "calculated_mass_flow_kg_s" in result
        assert "enthalpy_in_j_g" in result
        assert "enthalpy_out_j_g" in result
        assert "delta_h_j_g" in result
        assert "system_verification_status" in result

    def test_mass_flow_is_positive(self):
        result = verify_mass_balance(16.0)
        assert result["calculated_mass_flow_kg_s"] > 0.0

    def test_pass_status_for_nominal_load(self):
        result = verify_mass_balance(16.0)
        assert result["system_verification_status"] == "PASS"

    def test_warn_status_for_high_load(self):
        # Very large load should exceed warn limit
        result = verify_mass_balance(total_heat_load_w=50000.0)
        assert result["system_verification_status"] == "WARN_LIMIT"

    def test_enthalpy_out_greater_than_in(self):
        result = verify_mass_balance(16.0, t_in_k=4.2, t_out_k=4.5)
        assert result["enthalpy_out_j_g"] > result["enthalpy_in_j_g"]

    def test_delta_h_consistent(self):
        result = verify_mass_balance(16.0, t_in_k=4.2, t_out_k=4.5)
        expected_delta = round(result["enthalpy_out_j_g"] - result["enthalpy_in_j_g"], 3)
        assert abs(result["delta_h_j_g"] - expected_delta) < 0.01

    def test_raises_when_temperatures_equal(self):
        with pytest.raises(ValueError, match="zero"):
            verify_mass_balance(16.0, t_in_k=4.2, t_out_k=4.2)

    def test_custom_engine_accepted(self):
        engine = HeliumPropertyEngine()
        result = verify_mass_balance(16.0, engine=engine)
        assert result["calculated_mass_flow_kg_s"] > 0.0
