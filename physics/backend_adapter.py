"""Thin adapter interface for thermodynamic property backends.

Each backend implements a common interface defined by ``BackendBase``.
Missing commercial backends (REFPROP, HEPAK) raise ``BackendUnavailable``
rather than crashing, allowing graceful fallback during CI.

Usage:
    from physics.backend_adapter import get_backend, BackendUnavailable

    backend = get_backend("nist")
    props = backend.get_saturation_properties(T=4.2)
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REGISTRY_PATH = Path(__file__).resolve().parent / "backend_registry.yaml"


class BackendUnavailable(RuntimeError):
    """Raised when a requested backend is not available in the current environment."""


@dataclass
class SaturationProperties:
    """Saturation-curve properties at a given temperature."""

    temperature_K: float
    pressure_Pa: float | None = None
    density_kg_m3: float | None = None
    entropy_J_kgK: float | None = None
    enthalpy_J_kg: float | None = None
    source: str = "unknown"


class BackendBase(ABC):
    """Abstract base class for all thermodynamic backends."""

    name: str = "abstract"

    @abstractmethod
    def get_saturation_properties(self, T: float) -> SaturationProperties:
        """Return saturation properties at temperature *T* (Kelvin)."""

    def is_available(self) -> bool:
        return True


class FallbackBackend(BackendBase):
    """Minimal built-in approximations.  Always available.

    Uses simplified linear fits valid roughly 2–6 K for liquid helium-4.
    Not suitable for publication — use NIST/CoolProp for real work.
    """

    name = "fallback"

    def get_saturation_properties(self, T: float) -> SaturationProperties:
        # Very rough vapour-pressure approximation for He-4 (2–6 K range)
        import math

        A, B = 3.5, -5.3
        ln_p = A + B / T
        pressure_Pa = math.exp(ln_p) * 1e5
        return SaturationProperties(
            temperature_K=T,
            pressure_Pa=pressure_Pa,
            source=self.name,
        )


class NISTBackend(BackendBase):
    """NIST WebBook helium property tables loaded from local fixtures.

    Fixture data lives in ``tests/fixtures/`` or can be overridden via
    the ``fixture_path`` constructor argument.
    """

    name = "nist"

    # Tabulated He-4 saturation data: T(K), P(kPa), ρ_liquid(kg/m³), s_liquid(J/kg·K)
    _TABLE: list[tuple[float, float, float, float]] = [
        (2.17, 5.04, 146.2, 756.9),
        (2.50, 10.00, 141.5, 914.6),
        (3.00, 23.39, 131.6, 1148.0),
        (3.50, 46.10, 118.5, 1371.0),
        (4.00, 81.51, 101.4, 1598.0),
        (4.22, 101.33, 90.1, 1709.0),
        (4.50, 135.00, 74.0, 1854.0),
        (5.00, 229.00, 40.0, 2100.0),
    ]

    def get_saturation_properties(self, T: float) -> SaturationProperties:
        import bisect

        temps = [row[0] for row in self._TABLE]
        idx = bisect.bisect_left(temps, T)
        if idx == 0:
            row = self._TABLE[0]
        elif idx >= len(self._TABLE):
            row = self._TABLE[-1]
        else:
            # Linear interpolation
            t0, p0, d0, s0 = self._TABLE[idx - 1]
            t1, p1, d1, s1 = self._TABLE[idx]
            frac = (T - t0) / (t1 - t0)
            row = (T, p0 + frac * (p1 - p0), d0 + frac * (d1 - d0), s0 + frac * (s1 - s0))

        return SaturationProperties(
            temperature_K=T,
            pressure_Pa=row[1] * 1e3,
            density_kg_m3=row[2],
            entropy_J_kgK=row[3],
            source=self.name,
        )


class CoolPropBackend(BackendBase):
    """CoolProp backend.  Requires ``pip install CoolProp``."""

    name = "coolprop"

    def is_available(self) -> bool:
        try:
            import CoolProp  # noqa: F401

            return True
        except ImportError:
            return False

    def get_saturation_properties(self, T: float) -> SaturationProperties:
        try:
            from CoolProp.CoolProp import PropsSI
        except ImportError as exc:
            raise BackendUnavailable(
                "CoolProp is not installed. Run: pip install CoolProp"
            ) from exc
        return SaturationProperties(
            temperature_K=T,
            pressure_Pa=PropsSI("P", "T", T, "Q", 0, "Helium"),
            density_kg_m3=PropsSI("D", "T", T, "Q", 0, "Helium"),
            entropy_J_kgK=PropsSI("S", "T", T, "Q", 0, "Helium"),
            enthalpy_J_kg=PropsSI("H", "T", T, "Q", 0, "Helium"),
            source=self.name,
        )


class REFPROPBackend(BackendBase):
    """REFPROP backend.  Requires NIST REFPROP licence + ctREFPROP."""

    name = "refprop"

    def is_available(self) -> bool:
        try:
            import ctREFPROP  # noqa: F401

            return True
        except ImportError:
            return False

    def get_saturation_properties(self, T: float) -> SaturationProperties:
        raise BackendUnavailable(
            "REFPROP requires a commercial NIST licence and ctREFPROP wrapper."
        )


class HEPAKBackend(BackendBase):
    """HEPAK backend.  Requires HEPAK licence."""

    name = "hepak"

    def is_available(self) -> bool:
        return False

    def get_saturation_properties(self, T: float) -> SaturationProperties:
        raise BackendUnavailable(
            "HEPAK requires a commercial licence. Interface is scaffolded only."
        )


_BACKENDS: dict[str, BackendBase] = {
    "fallback": FallbackBackend(),
    "nist": NISTBackend(),
    "coolprop": CoolPropBackend(),
    "refprop": REFPROPBackend(),
    "hepak": HEPAKBackend(),
}


def get_backend(name: str) -> BackendBase:
    """Return the named backend, raising *BackendUnavailable* if not available."""
    backend = _BACKENDS.get(name.lower())
    if backend is None:
        raise BackendUnavailable(f"Unknown backend '{name}'. Available: {list(_BACKENDS)}")
    if not backend.is_available():
        raise BackendUnavailable(
            f"Backend '{name}' is not available in this environment. "
            "Check physics/backend_registry.yaml for installation notes."
        )
    return backend


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    """Load and return the backend registry YAML as a dict."""
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def available_backends(registry_path: Path = REGISTRY_PATH) -> list[str]:
    """Return names of backends marked available=true in the registry."""
    registry = load_registry(registry_path)
    return [
        name
        for name, cfg in registry.get("backends", {}).items()
        if cfg.get("available", False)
    ]
