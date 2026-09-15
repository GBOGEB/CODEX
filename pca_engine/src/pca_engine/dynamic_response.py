"""Declared continuous-time transfer-function response utilities.

The caller owns model structure, units and physical validity.  These functions
only simulate explicitly supplied SISO polynomial transfer functions.
"""
from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from .control_analytics import transfer_function_diagnostics


def _coefficients(values: Sequence[float], name: str) -> np.ndarray:
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or x.size == 0 or not np.isfinite(x).all():
        raise ValueError(f"{name} must be a non-empty finite coefficient vector")
    x = np.trim_zeros(x, "f")
    if x.size == 0:
        raise ValueError(f"{name} must not be identically zero")
    return x


def transfer_to_state_space(numerator: Sequence[float], denominator: Sequence[float]) -> dict[str, Any]:
    """Return controllable-canonical A,B,C,D for a proper SISO transfer function."""
    num = _coefficients(numerator, "numerator")
    den = _coefficients(denominator, "denominator")
    if den.size < 2:
        raise ValueError("a dynamic denominator of degree >= 1 is required")
    if num.size > den.size:
        raise ValueError("improper transfer functions are not supported")
    den = den / den[0]
    num = num / float(_coefficients(denominator, "denominator")[0])
    n = den.size - 1
    padded = np.pad(num, (den.size - num.size, 0))
    direct = float(padded[0])
    dynamic = padded[1:] - direct * den[1:]

    a = np.zeros((n, n), dtype=float)
    if n > 1:
        a[:-1, 1:] = np.eye(n - 1)
    a[-1, :] = -den[:0:-1]
    b = np.zeros(n, dtype=float)
    b[-1] = 1.0
    c = dynamic[::-1].astype(float)
    return {"A": a, "B": b, "C": c, "D": direct}


def _rk4_step(a: np.ndarray, b: np.ndarray, state: np.ndarray, dt: float, u: float = 1.0) -> np.ndarray:
    def derivative(x: np.ndarray) -> np.ndarray:
        return a @ x + b * u

    k1 = derivative(state)
    k2 = derivative(state + 0.5 * dt * k1)
    k3 = derivative(state + 0.5 * dt * k2)
    k4 = derivative(state + dt * k3)
    return state + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def step_response(
    numerator: Sequence[float],
    denominator: Sequence[float],
    *,
    duration: float | None = None,
    points: int = 1200,
    settling_band: float = 0.02,
) -> dict[str, Any]:
    """Numerically simulate a unit-step response using RK4.

    For stable systems, omitted duration is eight dominant time constants.  For
    marginal/unstable systems the caller must normally inspect the bounded
    diagnostic horizon rather than treat final values as steady state.
    """
    if points < 50:
        raise ValueError("points must be >= 50")
    if not 0.0 < settling_band < 1.0:
        raise ValueError("settling_band must be in (0,1)")
    diag = transfer_function_diagnostics(numerator, denominator)
    ss = transfer_to_state_space(numerator, denominator)
    a, b, c, d = ss["A"], ss["B"], ss["C"], float(ss["D"])
    dominant_tau = diag["dominant_time_constant"]
    if duration is None:
        duration = 8.0 * dominant_tau if dominant_tau is not None else 10.0
    duration = float(duration)
    if duration <= 0.0 or not np.isfinite(duration):
        raise ValueError("duration must be finite and > 0")

    time = np.linspace(0.0, duration, points)
    dt = float(time[1] - time[0])
    state = np.zeros(a.shape[0], dtype=float)
    response = np.empty(points, dtype=float)
    for i, _ in enumerate(time):
        response[i] = float(c @ state + d)
        if i + 1 < points:
            state = _rk4_step(a, b, state, dt)

    dc_gain = diag["dc_gain"]
    target = float(dc_gain) if dc_gain is not None and diag["stability_class"] == "STABLE" else float(response[-1])
    rise_time = None
    if abs(target) > np.finfo(float).eps:
        lo, hi = 0.1 * target, 0.9 * target
        if target > 0:
            i10 = np.flatnonzero(response >= lo)
            i90 = np.flatnonzero(response >= hi)
        else:
            i10 = np.flatnonzero(response <= lo)
            i90 = np.flatnonzero(response <= hi)
        if i10.size and i90.size and i90[0] >= i10[0]:
            rise_time = float(time[i90[0]] - time[i10[0]])

    settling_time = None
    if diag["stability_class"] == "STABLE" and abs(target) > np.finfo(float).eps:
        outside = np.flatnonzero(np.abs(response - target) > settling_band * abs(target))
        if outside.size == 0:
            settling_time = 0.0
        elif outside[-1] + 1 < points:
            settling_time = float(time[outside[-1] + 1])

    overshoot = None
    if abs(target) > np.finfo(float).eps:
        if target > 0:
            overshoot = max(0.0, (float(response.max()) - target) / abs(target) * 100.0)
        else:
            overshoot = max(0.0, (target - float(response.min())) / abs(target) * 100.0)

    return {
        "time": time.tolist(),
        "response": response.tolist(),
        "rise_time": rise_time,
        "settling_time": settling_time,
        "overshoot_percent": overshoot,
        "steady_reference": target,
        "model_diagnostics": diag,
        "authority": "DECLARED_MODEL_DIAGNOSTIC_ONLY",
    }
