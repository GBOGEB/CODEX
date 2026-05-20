"""Helium thermodynamic reference kernels.

These kernels provide analytical reference values for helium-4 based on
published NIST and GISTAU correlations.  They are intentionally simple and
explicit so they can be used for validation against licensed backends
(CoolProp, REFPROP, HEPAK) without introducing additional dependencies.

Reference data anchors:
  - Critical point: Tc = 5.1953 K, Pc = 227.46 kPa, rho_c = 69.64 kg/m³
  - Normal boiling point: T_nbp = 4.222 K at 101.325 kPa
  - Lambda point: T_lambda = 2.1768 K at 5.04 kPa
"""

from __future__ import annotations

# ── Helium-4 physical constants ──────────────────────────────────────────────

#: Critical temperature [K]
T_CRITICAL_K: float = 5.1953
#: Critical pressure [kPa]
P_CRITICAL_KPA: float = 227.46
#: Critical density [kg/m³]
RHO_CRITICAL_KG_M3: float = 69.64

#: Normal boiling point temperature at 101.325 kPa [K]
T_NBP_K: float = 4.222
#: Normal boiling pressure [kPa]
P_NBP_KPA: float = 101.325

#: Lambda transition temperature at saturation [K]
T_LAMBDA_K: float = 2.1768
#: Lambda transition pressure [kPa]
P_LAMBDA_KPA: float = 5.04

#: Molar mass of helium-4 [kg/mol]
MOLAR_MASS_KG_MOL: float = 4.002602e-3
#: Universal gas constant [J/(mol·K)]
R_UNIVERSAL_J_MOLK: float = 8.314462

#: Specific gas constant for helium-4 [J/(kg·K)]
R_SPECIFIC_J_KGK: float = R_UNIVERSAL_J_MOLK / MOLAR_MASS_KG_MOL


# ── NIST helium saturation data fixtures ─────────────────────────────────────
# Source: NIST WebBook / REFPROP ancillary values.
# These are fixed-point anchors used for validation regression; they are NOT
# intended to substitute for a real-fluid equation of state.

#: Selected NIST saturation anchor points [T_K, P_kPa, rho_liq_kg_m3,
#: rho_vap_kg_m3, h_liq_J_kg, h_vap_J_kg]
NIST_SATURATION_ANCHORS: tuple[tuple[float, ...], ...] = (
    #  T_K    P_kPa   rho_l   rho_v   h_l     h_v
    (2.177,   5.04,  146.6,   2.40,  -3270.0,  20100.0),
    (3.000,  35.31,  133.6,  12.50,   1740.0,  23200.0),
    (4.222, 101.32,  124.9,  16.89,   9900.0,  23500.0),
    (5.000, 193.80,  101.0,  36.60,  18900.0,  21000.0),
    (5.195, 227.46,   69.6,  69.64,  21700.0,  21700.0),
)


def ideal_gas_density(p_kpa: float, t_k: float) -> float:
    """Ideal-gas density approximation for helium [kg/m³].

    Parameters
    ----------
    p_kpa:
        Pressure [kPa].
    t_k:
        Temperature [K].

    Returns
    -------
    float
        Density [kg/m³].
    """
    if t_k <= 0.0:
        raise ValueError(f"Temperature must be positive, got {t_k} K")
    if p_kpa < 0.0:
        raise ValueError(f"Pressure must be non-negative, got {p_kpa} kPa")
    return (p_kpa * 1000.0) / (R_SPECIFIC_J_KGK * t_k)


def reduced_temperature(t_k: float) -> float:
    """Reduced temperature relative to the helium-4 critical point.

    Parameters
    ----------
    t_k:
        Temperature [K].
    """
    return t_k / T_CRITICAL_K


def reduced_pressure(p_kpa: float) -> float:
    """Reduced pressure relative to the helium-4 critical point.

    Parameters
    ----------
    p_kpa:
        Pressure [kPa].
    """
    return p_kpa / P_CRITICAL_KPA


def is_supercritical(p_kpa: float, t_k: float) -> bool:
    """Return True when the state is above the critical point."""
    return p_kpa > P_CRITICAL_KPA and t_k > T_CRITICAL_K


def saturation_pressure_approx(t_k: float) -> float:
    """Approximate helium-4 saturation pressure [kPa] via linear interpolation.

    Valid range: T_lambda (2.1768 K) ≤ T ≤ T_critical (5.1953 K).
    Uses NIST anchor points for interpolation; orientation-level accuracy
    only — use a real EOS for publication-grade values.

    Parameters
    ----------
    t_k:
        Temperature [K].

    Returns
    -------
    float
        Estimated saturation pressure [kPa].
    """
    if t_k < T_LAMBDA_K or t_k > T_CRITICAL_K:
        raise ValueError(
            f"Temperature {t_k} K is outside supported range "
            f"[{T_LAMBDA_K}, {T_CRITICAL_K}] K"
        )
    # Extract (T, P) pairs from NIST anchors in ascending T order
    anchors = sorted(NIST_SATURATION_ANCHORS, key=lambda r: r[0])
    t_vals = [r[0] for r in anchors]
    p_vals = [r[1] for r in anchors]

    # Linear interpolation between bracketing anchors
    for i in range(len(t_vals) - 1):
        t0, t1 = t_vals[i], t_vals[i + 1]
        if t0 <= t_k <= t1:
            frac = (t_k - t0) / max(t1 - t0, 1e-12)
            return p_vals[i] + frac * (p_vals[i + 1] - p_vals[i])

    # Boundary: return endpoint pressure
    return p_vals[0] if t_k <= t_vals[0] else p_vals[-1]


def nist_anchor_at_temperature(t_k: float, tolerance_k: float = 0.05) -> dict | None:
    """Return the NIST saturation anchor closest to *t_k*, or None.

    Parameters
    ----------
    t_k:
        Query temperature [K].
    tolerance_k:
        Maximum allowed deviation [K] before returning ``None``.

    Returns
    -------
    dict or None
        Keys: ``t_k``, ``p_kpa``, ``rho_liquid_kg_m3``, ``rho_vapor_kg_m3``,
        ``h_liquid_j_kg``, ``h_vapor_j_kg``.
    """
    best: tuple[float, ...] | None = None
    best_delta = float("inf")
    for row in NIST_SATURATION_ANCHORS:
        delta = abs(row[0] - t_k)
        if delta < best_delta:
            best_delta = delta
            best = row
    if best is None or best_delta > tolerance_k:
        return None
    return {
        "t_k": best[0],
        "p_kpa": best[1],
        "rho_liquid_kg_m3": best[2],
        "rho_vapor_kg_m3": best[3],
        "h_liquid_j_kg": best[4],
        "h_vapor_j_kg": best[5],
    }
