"""Tests for physics/helium_refrigeration_core.py governance validation logic."""

from __future__ import annotations

import sys
from pathlib import Path
from decimal import Decimal
import tempfile
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from physics import helium_refrigeration_core as core


def test_verify_mass_fractions_pass_exact() -> None:
    """Test mass fraction validation passes for exact sum to 1.0000."""
    fractions = [0.9995, 0.0005]
    assert core.verify_mass_fractions(fractions) is True


def test_verify_mass_fractions_pass_with_rounding() -> None:
    """Test mass fraction validation passes when values round to 1.0000."""
    # Example: precise values that round/quantize to exactly 1.0000 at 4 decimals
    fractions = [0.500001, 0.499999]  # Both round to 0.5000, sum = 1.0000
    assert core.verify_mass_fractions(fractions) is True


def test_verify_mass_fractions_fail_underflow() -> None:
    """Test mass fraction validation fails when sum < 1.0000."""
    fractions = [0.9990, 0.0005]
    assert core.verify_mass_fractions(fractions) is False


def test_verify_mass_fractions_fail_overflow() -> None:
    """Test mass fraction validation fails when sum > 1.0000."""
    fractions = [0.9996, 0.0005]
    assert core.verify_mass_fractions(fractions) is False


def test_verify_mass_fractions_decimal_determinism() -> None:
    """Test that Decimal arithmetic is deterministic for edge cases."""
    # This would fail with float rounding: sum([0.1]*10) != 1.0
    fractions = [0.1] * 10
    assert core.verify_mass_fractions(fractions) is True


def test_validate_2k_static_benchmark_pass() -> None:
    """Test 2K-SB validation passes when efficiency meets target."""
    assert core.validate_2k_static_benchmark(0.3620, 0.35) is True


def test_validate_2k_static_benchmark_exact_match() -> None:
    """Test 2K-SB validation passes for exact match."""
    assert core.validate_2k_static_benchmark(0.35, 0.35) is True


def test_validate_2k_static_benchmark_fail() -> None:
    """Test 2K-SB validation fails when efficiency below target."""
    assert core.validate_2k_static_benchmark(0.34, 0.35) is False


def test_validate_2k_operational_flow_pass_within_tolerance() -> None:
    """Test 2K-OP validation passes when flow within default 5% tolerance."""
    assert core.validate_2k_operational_flow(11.4850, 11.5) is True


def test_validate_2k_operational_flow_pass_at_upper_bound() -> None:
    """Test 2K-OP validation passes at upper tolerance bound."""
    assert core.validate_2k_operational_flow(12.075, 11.5, tolerance=0.05) is True


def test_validate_2k_operational_flow_pass_at_lower_bound() -> None:
    """Test 2K-OP validation passes at lower tolerance bound."""
    assert core.validate_2k_operational_flow(10.925, 11.5, tolerance=0.05) is True


def test_validate_2k_operational_flow_fail_above_tolerance() -> None:
    """Test 2K-OP validation fails when flow exceeds upper tolerance."""
    assert core.validate_2k_operational_flow(12.1, 11.5, tolerance=0.05) is False


def test_validate_2k_operational_flow_fail_below_tolerance() -> None:
    """Test 2K-OP validation fails when flow below lower tolerance."""
    assert core.validate_2k_operational_flow(10.9, 11.5, tolerance=0.05) is False


def test_run_governance_assimilation_pass(tmp_path: Path) -> None:
    """Test full governance assimilation passes with valid SSOT and inputs."""
    ssot_file = tmp_path / "test_ssot.yaml"
    ssot_file.write_text("""
ssot:
  components:
    - id: G10-TUPLE-HE-REF
      modes:
        2K-SB:
          target_efficiency: 0.35
        2K-OP:
          nominal_flow_g_s: 11.5
""")
    
    result = core.run_governance_assimilation(
        ssot_path=str(ssot_file),
        active_flow=11.4850,
        active_efficiency=0.3620,
        mass_mix=[0.9995, 0.0005],
    )
    assert result is True


def test_run_governance_assimilation_fail_missing_file() -> None:
    """Test governance fails gracefully when SSOT file doesn't exist."""
    result = core.run_governance_assimilation(
        ssot_path="/nonexistent/path.yaml",
        active_flow=11.5,
        active_efficiency=0.36,
        mass_mix=[0.9995, 0.0005],
    )
    assert result is False


def test_run_governance_assimilation_fail_empty_file(tmp_path: Path) -> None:
    """Test governance fails when SSOT file is empty."""
    ssot_file = tmp_path / "empty.yaml"
    ssot_file.write_text("")
    
    result = core.run_governance_assimilation(
        ssot_path=str(ssot_file),
        active_flow=11.5,
        active_efficiency=0.36,
        mass_mix=[0.9995, 0.0005],
    )
    assert result is False


def test_run_governance_assimilation_fail_non_dict_yaml(tmp_path: Path) -> None:
    """Test governance fails when YAML is not a dict."""
    ssot_file = tmp_path / "invalid.yaml"
    ssot_file.write_text("- item1\n- item2\n")
    
    result = core.run_governance_assimilation(
        ssot_path=str(ssot_file),
        active_flow=11.5,
        active_efficiency=0.36,
        mass_mix=[0.9995, 0.0005],
    )
    assert result is False


def test_run_governance_assimilation_fail_malformed_yaml_syntax(tmp_path: Path) -> None:
    """Test governance fails gracefully when YAML has syntax errors."""
    ssot_file = tmp_path / "syntax_error.yaml"
    ssot_file.write_text("invalid: yaml: syntax:\n  - broken\n  indentation")
    
    result = core.run_governance_assimilation(
        ssot_path=str(ssot_file),
        active_flow=11.5,
        active_efficiency=0.36,
        mass_mix=[0.9995, 0.0005],
    )
    assert result is False


def test_run_governance_assimilation_fail_missing_ssot_root(tmp_path: Path) -> None:
    """Test governance fails when 'ssot' root key is missing."""
    ssot_file = tmp_path / "no_root.yaml"
    ssot_file.write_text("components: []")
    
    result = core.run_governance_assimilation(
        ssot_path=str(ssot_file),
        active_flow=11.5,
        active_efficiency=0.36,
        mass_mix=[0.9995, 0.0005],
    )
    assert result is False


def test_run_governance_assimilation_fail_missing_components(tmp_path: Path) -> None:
    """Test governance fails when 'components' list is missing."""
    ssot_file = tmp_path / "no_components.yaml"
    ssot_file.write_text("ssot:\n  version: 1.0")
    
    result = core.run_governance_assimilation(
        ssot_path=str(ssot_file),
        active_flow=11.5,
        active_efficiency=0.36,
        mass_mix=[0.9995, 0.0005],
    )
    assert result is False


def test_run_governance_assimilation_fail_component_not_found(tmp_path: Path) -> None:
    """Test governance fails when target component ID not in SSOT."""
    ssot_file = tmp_path / "wrong_component.yaml"
    ssot_file.write_text("""
ssot:
  components:
    - id: WRONG-ID
      modes: {}
""")
    
    result = core.run_governance_assimilation(
        ssot_path=str(ssot_file),
        active_flow=11.5,
        active_efficiency=0.36,
        mass_mix=[0.9995, 0.0005],
    )
    assert result is False


def test_run_governance_assimilation_fail_missing_modes(tmp_path: Path) -> None:
    """Test governance fails when 'modes' key is missing."""
    ssot_file = tmp_path / "no_modes.yaml"
    ssot_file.write_text("""
ssot:
  components:
    - id: G10-TUPLE-HE-REF
      description: test
""")
    
    result = core.run_governance_assimilation(
        ssot_path=str(ssot_file),
        active_flow=11.5,
        active_efficiency=0.36,
        mass_mix=[0.9995, 0.0005],
    )
    assert result is False


def test_run_governance_assimilation_fail_missing_2k_sb_mode(tmp_path: Path) -> None:
    """Test governance fails when '2K-SB' mode is missing."""
    ssot_file = tmp_path / "no_2k_sb.yaml"
    ssot_file.write_text("""
ssot:
  components:
    - id: G10-TUPLE-HE-REF
      modes:
        2K-OP:
          nominal_flow_g_s: 11.5
""")
    
    result = core.run_governance_assimilation(
        ssot_path=str(ssot_file),
        active_flow=11.5,
        active_efficiency=0.36,
        mass_mix=[0.9995, 0.0005],
    )
    assert result is False


def test_run_governance_assimilation_fail_missing_2k_op_mode(tmp_path: Path) -> None:
    """Test governance fails when '2K-OP' mode is missing."""
    ssot_file = tmp_path / "no_2k_op.yaml"
    ssot_file.write_text("""
ssot:
  components:
    - id: G10-TUPLE-HE-REF
      modes:
        2K-SB:
          target_efficiency: 0.35
""")
    
    result = core.run_governance_assimilation(
        ssot_path=str(ssot_file),
        active_flow=11.5,
        active_efficiency=0.36,
        mass_mix=[0.9995, 0.0005],
    )
    assert result is False


def test_run_governance_assimilation_fail_missing_target_efficiency(tmp_path: Path) -> None:
    """Test governance fails when 'target_efficiency' parameter is missing."""
    ssot_file = tmp_path / "no_target_eff.yaml"
    ssot_file.write_text("""
ssot:
  components:
    - id: G10-TUPLE-HE-REF
      modes:
        2K-SB:
          description: test
        2K-OP:
          nominal_flow_g_s: 11.5
""")
    
    result = core.run_governance_assimilation(
        ssot_path=str(ssot_file),
        active_flow=11.5,
        active_efficiency=0.36,
        mass_mix=[0.9995, 0.0005],
    )
    assert result is False


def test_run_governance_assimilation_fail_missing_nominal_flow(tmp_path: Path) -> None:
    """Test governance fails when 'nominal_flow_g_s' parameter is missing."""
    ssot_file = tmp_path / "no_flow.yaml"
    ssot_file.write_text("""
ssot:
  components:
    - id: G10-TUPLE-HE-REF
      modes:
        2K-SB:
          target_efficiency: 0.35
        2K-OP:
          description: test
""")
    
    result = core.run_governance_assimilation(
        ssot_path=str(ssot_file),
        active_flow=11.5,
        active_efficiency=0.36,
        mass_mix=[0.9995, 0.0005],
    )
    assert result is False


def test_run_governance_assimilation_fail_mass_fraction_gate(tmp_path: Path) -> None:
    """Test governance fails when mass fraction gate fails."""
    ssot_file = tmp_path / "test_ssot.yaml"
    ssot_file.write_text("""
ssot:
  components:
    - id: G10-TUPLE-HE-REF
      modes:
        2K-SB:
          target_efficiency: 0.35
        2K-OP:
          nominal_flow_g_s: 11.5
""")
    
    result = core.run_governance_assimilation(
        ssot_path=str(ssot_file),
        active_flow=11.4850,
        active_efficiency=0.3620,
        mass_mix=[0.9990, 0.0005],  # Sum != 1.0000
    )
    assert result is False


def test_run_governance_assimilation_fail_efficiency_gate(tmp_path: Path) -> None:
    """Test governance fails when 2K-SB efficiency gate fails."""
    ssot_file = tmp_path / "test_ssot.yaml"
    ssot_file.write_text("""
ssot:
  components:
    - id: G10-TUPLE-HE-REF
      modes:
        2K-SB:
          target_efficiency: 0.35
        2K-OP:
          nominal_flow_g_s: 11.5
""")
    
    result = core.run_governance_assimilation(
        ssot_path=str(ssot_file),
        active_flow=11.4850,
        active_efficiency=0.34,  # Below 0.35 target
        mass_mix=[0.9995, 0.0005],
    )
    assert result is False


def test_run_governance_assimilation_fail_flow_gate(tmp_path: Path) -> None:
    """Test governance fails when 2K-OP flow gate fails."""
    ssot_file = tmp_path / "test_ssot.yaml"
    ssot_file.write_text("""
ssot:
  components:
    - id: G10-TUPLE-HE-REF
      modes:
        2K-SB:
          target_efficiency: 0.35
        2K-OP:
          nominal_flow_g_s: 11.5
""")
    
    result = core.run_governance_assimilation(
        ssot_path=str(ssot_file),
        active_flow=12.5,  # Outside 5% tolerance
        active_efficiency=0.3620,
        mass_mix=[0.9995, 0.0005],
    )
    assert result is False
