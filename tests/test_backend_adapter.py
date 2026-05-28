"""Tests for physics/backend_adapter.py.

All tests use mocking or the always-available FallbackBackend/NISTBackend;
no commercial licences (REFPROP, HEPAK) are required.
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from physics.backend_adapter import (
    BackendUnavailable,
    CoolPropBackend,
    FallbackBackend,
    HEPAKBackend,
    NISTBackend,
    REFPROPBackend,
    SaturationProperties,
    available_backends,
    get_backend,
    load_registry,
)


# ---------------------------------------------------------------------------
# SaturationProperties dataclass
# ---------------------------------------------------------------------------


class TestSaturationProperties:
    def test_required_field_only(self) -> None:
        p = SaturationProperties(temperature_K=4.2)
        assert p.temperature_K == 4.2
        assert p.pressure_Pa is None
        assert p.source == "unknown"

    def test_all_fields(self) -> None:
        p = SaturationProperties(
            temperature_K=4.22,
            pressure_Pa=101330.0,
            density_kg_m3=90.1,
            entropy_J_kgK=1709.0,
            enthalpy_J_kg=None,
            source="nist",
        )
        assert p.source == "nist"
        assert p.density_kg_m3 == pytest.approx(90.1)


# ---------------------------------------------------------------------------
# FallbackBackend
# ---------------------------------------------------------------------------


class TestFallbackBackend:
    def test_is_always_available(self) -> None:
        assert FallbackBackend().is_available() is True

    def test_returns_saturation_properties(self) -> None:
        props = FallbackBackend().get_saturation_properties(4.2)
        assert isinstance(props, SaturationProperties)
        assert props.temperature_K == pytest.approx(4.2)
        assert props.pressure_Pa is not None
        assert props.pressure_Pa > 0
        assert props.source == "fallback"

    def test_pressure_increases_with_temperature(self) -> None:
        fb = FallbackBackend()
        p_low = fb.get_saturation_properties(3.0).pressure_Pa
        p_high = fb.get_saturation_properties(5.0).pressure_Pa
        assert p_high > p_low


# ---------------------------------------------------------------------------
# NISTBackend
# ---------------------------------------------------------------------------


class TestNISTBackend:
    def test_is_available(self) -> None:
        assert NISTBackend().is_available() is True

    def test_known_point_boiling_at_1_atm(self) -> None:
        props = NISTBackend().get_saturation_properties(4.22)
        assert props.temperature_K == pytest.approx(4.22)
        assert props.pressure_Pa == pytest.approx(101330.0, rel=1e-3)
        assert props.density_kg_m3 == pytest.approx(90.1, rel=1e-3)
        assert props.entropy_J_kgK == pytest.approx(1709.0, rel=1e-3)
        assert props.source == "nist"

    def test_interpolation_between_table_points(self) -> None:
        props = NISTBackend().get_saturation_properties(3.25)
        assert 3.0 < props.temperature_K < 3.5
        assert props.pressure_Pa is not None
        assert props.density_kg_m3 is not None

    def test_clamps_below_table(self) -> None:
        props = NISTBackend().get_saturation_properties(1.0)
        assert props.pressure_Pa is not None

    def test_clamps_above_table(self) -> None:
        props = NISTBackend().get_saturation_properties(10.0)
        assert props.pressure_Pa is not None


# ---------------------------------------------------------------------------
# CoolPropBackend
# ---------------------------------------------------------------------------


class TestCoolPropBackend:
    def test_unavailable_when_not_installed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(sys.modules, "CoolProp", None)
        backend = CoolPropBackend()
        assert backend.is_available() is False

    def test_raises_backend_unavailable_when_not_installed(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(sys.modules, "CoolProp", None)
        monkeypatch.setitem(sys.modules, "CoolProp.CoolProp", None)
        with pytest.raises(BackendUnavailable, match="CoolProp"):
            CoolPropBackend().get_saturation_properties(4.2)

    def test_delegates_to_coolprop_propsi_when_available(self) -> None:
        mock_coolprop = MagicMock()
        mock_coolprop.CoolProp.PropsSI.return_value = 100000.0
        with patch.dict(
            sys.modules,
            {"CoolProp": mock_coolprop, "CoolProp.CoolProp": mock_coolprop.CoolProp},
        ):
            backend = CoolPropBackend()
            props = backend.get_saturation_properties(4.2)
        assert props.source == "coolprop"
        assert props.temperature_K == pytest.approx(4.2)


# ---------------------------------------------------------------------------
# REFPROPBackend
# ---------------------------------------------------------------------------


class TestREFPROPBackend:
    def test_unavailable_without_licence(self) -> None:
        assert REFPROPBackend().is_available() is False

    def test_raises_backend_unavailable(self) -> None:
        with pytest.raises(BackendUnavailable, match="REFPROP"):
            REFPROPBackend().get_saturation_properties(4.2)


# ---------------------------------------------------------------------------
# HEPAKBackend
# ---------------------------------------------------------------------------


class TestHEPAKBackend:
    def test_unavailable(self) -> None:
        assert HEPAKBackend().is_available() is False

    def test_raises_backend_unavailable(self) -> None:
        with pytest.raises(BackendUnavailable, match="HEPAK"):
            HEPAKBackend().get_saturation_properties(4.2)


# ---------------------------------------------------------------------------
# get_backend
# ---------------------------------------------------------------------------


class TestGetBackend:
    def test_returns_fallback(self) -> None:
        backend = get_backend("fallback")
        assert isinstance(backend, FallbackBackend)

    def test_returns_nist(self) -> None:
        backend = get_backend("nist")
        assert isinstance(backend, NISTBackend)

    def test_case_insensitive(self) -> None:
        backend = get_backend("NIST")
        assert isinstance(backend, NISTBackend)

    def test_unknown_name_raises(self) -> None:
        with pytest.raises(BackendUnavailable, match="Unknown backend"):
            get_backend("unknown_xyz")

    def test_unavailable_backend_raises(self) -> None:
        with pytest.raises(BackendUnavailable):
            get_backend("hepak")


# ---------------------------------------------------------------------------
# load_registry and available_backends
# ---------------------------------------------------------------------------


class TestLoadRegistry:
    def test_loads_default_registry(self) -> None:
        registry = load_registry()
        assert "backends" in registry
        assert "fallback" in registry["backends"]

    def test_loads_custom_registry(self, tmp_path: Path) -> None:
        custom = tmp_path / "registry.yaml"
        custom.write_text(
            textwrap.dedent(
                """\
                version: 1
                backends:
                  test_backend:
                    available: true
                    version: "0.1"
                    entrypoint: "test"
                    description: "test"
                    capabilities: []
                """
            ),
            encoding="utf-8",
        )
        registry = load_registry(custom)
        assert "test_backend" in registry["backends"]


class TestAvailableBackends:
    def test_includes_fallback_and_nist(self) -> None:
        backends = available_backends()
        assert "fallback" in backends
        assert "nist" in backends

    def test_excludes_commercial_backends(self) -> None:
        backends = available_backends()
        assert "hepak" not in backends
        assert "refprop" not in backends

    def test_custom_registry(self, tmp_path: Path) -> None:
        custom = tmp_path / "registry.yaml"
        custom.write_text(
            textwrap.dedent(
                """\
                version: 1
                backends:
                  alpha:
                    available: true
                    version: "1"
                    entrypoint: "x"
                    description: "a"
                    capabilities: []
                  beta:
                    available: false
                    version: "1"
                    entrypoint: "y"
                    description: "b"
                    capabilities: []
                """
            ),
            encoding="utf-8",
        )
        result = available_backends(custom)
        assert result == ["alpha"]
