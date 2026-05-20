"""Saturation dome reconstruction kernels for helium-4.

Provides deterministic sampling of the helium-4 saturation dome (T-s plane)
using NIST anchor data and lightweight interpolation.  The module is
intentionally backend-free so it can run in CI without REFPROP or HEPAK.

The saturation dome is critical for:
  - T-s diagram validation (GISTAU Chapter 15 figures)
  - Two-phase quality calculation
  - He-II / lambda-region boundary indication
"""

from __future__ import annotations

from dataclasses import dataclass

from .helium_reference import (
    NIST_SATURATION_ANCHORS,
    T_CRITICAL_K,
    T_LAMBDA_K,
)


@dataclass(frozen=True)
class SaturationPoint:
    """One point on the helium-4 saturation dome.

    Parameters
    ----------
    temperature_k:
        Saturation temperature [K].
    pressure_kpa:
        Saturation pressure [kPa].
    entropy_liquid_j_kgk:
        Specific entropy of the saturated liquid [J/(kg·K)].
    entropy_vapor_j_kgk:
        Specific entropy of the saturated vapor [J/(kg·K)].
    enthalpy_liquid_j_kg:
        Specific enthalpy of the saturated liquid [J/kg].
    enthalpy_vapor_j_kg:
        Specific enthalpy of the saturated vapor [J/kg].
    """

    temperature_k: float
    pressure_kpa: float
    entropy_liquid_j_kgk: float
    entropy_vapor_j_kgk: float
    enthalpy_liquid_j_kg: float
    enthalpy_vapor_j_kg: float

    @property
    def latent_heat_j_kg(self) -> float:
        """Heat of vaporisation [J/kg]."""
        return self.enthalpy_vapor_j_kg - self.enthalpy_liquid_j_kg

    @property
    def entropy_span_j_kgk(self) -> float:
        """Difference between vapor and liquid entropy [J/(kg·K)]."""
        return self.entropy_vapor_j_kgk - self.entropy_liquid_j_kgk


# ── Deterministic NIST-anchor saturation dome ────────────────────────────────
# These entropy estimates are derived from Clausius-Clapeyron:
#   Δs ≈ Δh / T
# and anchored to the NIST enthalpy values stored in helium_reference.py.
# They are orientation-level estimates; use a real EOS for publication.

def _estimate_entropy_span(h_liq: float, h_vap: float, t_k: float) -> tuple[float, float]:
    """Estimate liquid and vapor entropy using Clausius-Clapeyron.

    Parameters
    ----------
    h_liq, h_vap:
        Saturated liquid/vapor enthalpies [J/kg].
    t_k:
        Saturation temperature [K].

    Returns
    -------
    (s_liq, s_vap) in J/(kg·K)
    """
    delta_h = h_vap - h_liq
    delta_s = delta_h / max(t_k, 1e-9)
    # Anchor liquid entropy to an approximate absolute value.
    # At the normal boiling point (4.222 K, 101.325 kPa) literature gives
    # s_liq ≈ 2.2 kJ/(kg·K) and s_vap ≈ 7.8 kJ/(kg·K).
    T_NBP = 4.222
    S_LIQ_NBP = 2200.0   # J/(kg·K)
    # Scale liquid entropy linearly with temperature as a first approximation.
    s_liq = S_LIQ_NBP * (t_k / T_NBP)
    s_vap = s_liq + delta_s
    return s_liq, s_vap


def build_nist_dome() -> list[SaturationPoint]:
    """Build a list of :class:`SaturationPoint` from NIST anchor data.

    Returns the points in ascending temperature order.  The critical point
    entry is included as a single degenerate point where liquid = vapor.
    """
    points: list[SaturationPoint] = []
    for row in sorted(NIST_SATURATION_ANCHORS, key=lambda r: r[0]):
        t_k, p_kpa, _rho_l, _rho_v, h_liq, h_vap = row
        s_liq, s_vap = _estimate_entropy_span(h_liq, h_vap, t_k)
        points.append(
            SaturationPoint(
                temperature_k=t_k,
                pressure_kpa=p_kpa,
                entropy_liquid_j_kgk=s_liq,
                entropy_vapor_j_kgk=s_vap,
                enthalpy_liquid_j_kg=h_liq,
                enthalpy_vapor_j_kg=h_vap,
            )
        )
    return points


def sample_dome(
    n_points: int = 20,
    t_min_k: float = T_LAMBDA_K,
    t_max_k: float = T_CRITICAL_K,
) -> list[SaturationPoint]:
    """Interpolate the saturation dome between *t_min_k* and *t_max_k*.

    Uses the NIST anchor points as control nodes and performs linear
    interpolation in temperature space.

    Parameters
    ----------
    n_points:
        Number of points to sample.
    t_min_k:
        Lower temperature bound [K].  Defaults to the lambda point.
    t_max_k:
        Upper temperature bound [K].  Defaults to the critical temperature.

    Returns
    -------
    list[SaturationPoint]
        Points in ascending temperature order.
    """
    if n_points < 2:
        raise ValueError(f"n_points must be >= 2, got {n_points}")
    if t_min_k >= t_max_k:
        raise ValueError(
            f"t_min_k ({t_min_k}) must be less than t_max_k ({t_max_k})"
        )

    anchors = build_nist_dome()
    t_anchors = [p.temperature_k for p in anchors]

    def _interp_scalar(t: float, y_key: str) -> float:
        vals = [getattr(p, y_key) for p in anchors]
        # Find surrounding pair
        for i in range(len(t_anchors) - 1):
            t0, t1 = t_anchors[i], t_anchors[i + 1]
            if t0 <= t <= t1:
                frac = (t - t0) / max(t1 - t0, 1e-12)
                return vals[i] + frac * (vals[i + 1] - vals[i])
        # Extrapolate at boundaries
        if t <= t_anchors[0]:
            return vals[0]
        return vals[-1]

    step = (t_max_k - t_min_k) / (n_points - 1)
    result: list[SaturationPoint] = []
    for i in range(n_points):
        t = t_min_k + i * step
        result.append(
            SaturationPoint(
                temperature_k=t,
                pressure_kpa=_interp_scalar(t, "pressure_kpa"),
                entropy_liquid_j_kgk=_interp_scalar(t, "entropy_liquid_j_kgk"),
                entropy_vapor_j_kgk=_interp_scalar(t, "entropy_vapor_j_kgk"),
                enthalpy_liquid_j_kg=_interp_scalar(t, "enthalpy_liquid_j_kg"),
                enthalpy_vapor_j_kg=_interp_scalar(t, "enthalpy_vapor_j_kg"),
            )
        )
    return result
