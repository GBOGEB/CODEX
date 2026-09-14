"""Generic empirical-control analytics for evidence-aware engineering workflows.

This module is deliberately non-authoritative: it computes statistical, matrix,
PCA-pressure, convergence, spectral and declared dynamic-model diagnostics.  It
must not be used to promote source evidence, acceptance, compliance or release
state by itself.
"""
from __future__ import annotations

from statistics import NormalDist
from typing import Any, Iterable, Sequence

import numpy as np

from .pca_core import PCAResult
from .pca_loadings import loadings


def _finite_1d(values: Iterable[float], *, name: str = "values") -> np.ndarray:
    x = np.asarray(list(values), dtype=float)
    if x.ndim != 1 or x.size == 0:
        raise ValueError(f"{name} must be a non-empty one-dimensional sequence")
    if not np.isfinite(x).all():
        raise ValueError(f"{name} must contain only finite values")
    return x


def _finite_2d(values: Any, *, name: str = "matrix") -> np.ndarray:
    x = np.asarray(values, dtype=float)
    if x.ndim != 2 or min(x.shape) == 0:
        raise ValueError(f"{name} must be a non-empty two-dimensional matrix")
    if not np.isfinite(x).all():
        raise ValueError(f"{name} must contain only finite values")
    return x


def lu_decomposition(matrix: Any) -> dict[str, Any]:
    """Partial-pivoting LU decomposition using NumPy only.

    Returns P, L, U satisfying P @ A ~= L @ U plus the reconstruction error.
    """
    a = _finite_2d(matrix)
    if a.shape[0] != a.shape[1]:
        raise ValueError("LU decomposition requires a square matrix")
    n = a.shape[0]
    u = a.copy()
    l = np.eye(n)
    p = np.eye(n)
    for k in range(n - 1):
        pivot = k + int(np.argmax(np.abs(u[k:, k])))
        if abs(u[pivot, k]) <= np.finfo(float).eps:
            continue
        if pivot != k:
            u[[k, pivot]] = u[[pivot, k]]
            p[[k, pivot]] = p[[pivot, k]]
            if k:
                l[[k, pivot], :k] = l[[pivot, k], :k]
        for i in range(k + 1, n):
            if abs(u[k, k]) <= np.finfo(float).eps:
                continue
            factor = u[i, k] / u[k, k]
            l[i, k] = factor
            u[i, k:] -= factor * u[k, k:]
    error = float(np.linalg.norm(p @ a - l @ u, ord="fro"))
    return {"P": p.tolist(), "L": l.tolist(), "U": u.tolist(), "reconstruction_error": error}


def matrix_diagnostics(data: Any) -> dict[str, Any]:
    """Return covariance/eigen/SVD/QR and conditioning diagnostics.

    Rows are observations and columns are variables.  Determinant/log-determinant
    refer to the covariance matrix, not to a physical invariant.
    """
    x = _finite_2d(data)
    if x.shape[0] < 2:
        raise ValueError("matrix diagnostics require at least two observations")
    covariance = np.atleast_2d(np.cov(x, rowvar=False, ddof=1))
    correlation = np.nan_to_num(np.atleast_2d(np.corrcoef(x, rowvar=False)), nan=0.0)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    singular_values = np.linalg.svd(x - x.mean(axis=0), compute_uv=False)
    q, r = np.linalg.qr(x - x.mean(axis=0), mode="reduced")
    sign, logabsdet = np.linalg.slogdet(covariance)
    determinant = float(np.linalg.det(covariance))
    rank = int(np.linalg.matrix_rank(covariance))
    condition = float(np.linalg.cond(covariance))
    positive = np.clip(eigenvalues, 0.0, None)
    total = float(positive.sum())
    evr = positive / total if total > 0.0 else np.zeros_like(positive)
    return {
        "covariance_matrix": covariance.tolist(),
        "correlation_matrix": correlation.tolist(),
        "determinant": determinant,
        "slogdet_sign": float(sign),
        "log_abs_determinant": float(logabsdet),
        "numerical_rank": rank,
        "condition_number": condition,
        "near_singular": bool((not np.isfinite(condition)) or condition >= 1.0e10),
        "eigenvalues": eigenvalues.tolist(),
        "eigenvectors": eigenvectors.tolist(),
        "explained_variance_ratio": evr.tolist(),
        "singular_values": singular_values.tolist(),
        "qr": {"Q": q.tolist(), "R": r.tolist()},
        "authority": "DIAGNOSTIC_ONLY",
    }


def confidence_interval(
    values: Iterable[float],
    *,
    confidence: float = 0.95,
    method: str = "normal",
    bootstrap_samples: int = 4000,
    seed: int = 0,
) -> dict[str, Any]:
    """Confidence interval for the mean with explicit method/assumptions.

    `normal` uses a normal critical value with sample standard error.  `bootstrap`
    uses a deterministic percentile bootstrap and makes no normality claim.
    """
    x = _finite_1d(values)
    if x.size < 2:
        raise ValueError("confidence interval requires at least two observations")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be in (0,1)")
    estimate = float(x.mean())
    alpha = 1.0 - confidence
    if method == "normal":
        z = NormalDist().inv_cdf(1.0 - alpha / 2.0)
        se = float(x.std(ddof=1) / np.sqrt(x.size))
        low, high = estimate - z * se, estimate + z * se
        assumptions = ["independent-or-effective-independent observations", "normal approximation for the mean"]
    elif method == "bootstrap":
        if bootstrap_samples < 200:
            raise ValueError("bootstrap_samples must be >= 200")
        rng = np.random.default_rng(seed)
        samples = rng.choice(x, size=(bootstrap_samples, x.size), replace=True).mean(axis=1)
        low, high = np.quantile(samples, [alpha / 2.0, 1.0 - alpha / 2.0])
        se = float(samples.std(ddof=1))
        assumptions = ["iid resampling unless caller has already formed effective/block observations"]
    else:
        raise ValueError("method must be 'normal' or 'bootstrap'")
    return {
        "estimate": estimate,
        "confidence_level": confidence,
        "lower_bound": float(low),
        "upper_bound": float(high),
        "standard_error": se,
        "sample_count": int(x.size),
        "method": method,
        "assumptions": assumptions,
        "authority": "STATISTICAL_EVIDENCE_ONLY",
    }


def sigma_crossings(
    values: Iterable[float],
    *,
    baseline_mean: float | None = None,
    baseline_std: float | None = None,
    thresholds: Sequence[float] = (3.0, 4.0, 5.0, 6.0),
) -> dict[str, Any]:
    """Compute signed z-scores and 3/4/5/6-sigma threshold-entry receipts."""
    x = _finite_1d(values)
    mu = float(x.mean()) if baseline_mean is None else float(baseline_mean)
    if baseline_std is None:
        if x.size < 2:
            raise ValueError("baseline_std is required for a single observation")
        sigma = float(x.std(ddof=1))
        baseline_method = "same-series sample mean/std"
    else:
        sigma = float(baseline_std)
        baseline_method = "caller-supplied baseline"
    if not np.isfinite(mu) or not np.isfinite(sigma) or sigma <= 0.0:
        raise ValueError("baseline mean/std must be finite and std > 0")
    levels = sorted(float(t) for t in thresholds)
    if not levels or levels[0] <= 0.0:
        raise ValueError("thresholds must be positive")
    receipts = []
    counts = {str(t): 0 for t in levels}
    for index, value in enumerate(x):
        z = (float(value) - mu) / sigma
        entered = [t for t in levels if abs(z) >= t]
        highest = max(entered) if entered else None
        for t in entered:
            counts[str(t)] += 1
        receipts.append(
            {
                "index": index,
                "value": float(value),
                "z_score": z,
                "direction": "HIGH" if z > 0 else "LOW" if z < 0 else "ON_MEAN",
                "highest_threshold_entered": highest,
                "entered_thresholds": entered,
            }
        )
    return {
        "baseline_mean": mu,
        "baseline_std": sigma,
        "baseline_method": baseline_method,
        "threshold_counts": counts,
        "receipts": receipts,
        "guard": "sigma crossing is a control diagnostic, not engineering closure or Six Sigma process capability",
    }


def reverse_pressure(
    result: PCAResult,
    *,
    mode_pressure: Sequence[float] | None = None,
    source_gap: Sequence[float] | None = None,
) -> dict[str, Any]:
    """Back-project unresolved mode pressure to original features.

    This is intentionally separate from Bradley-Terry.  By default each retained
    mode receives pressure 1.0; caller pressure can encode unresolved gap/DMAIC
    state externally.  Contributions are weighted by explained variance.
    """
    n = result.n_components_
    pressure = np.ones(n) if mode_pressure is None else np.asarray(mode_pressure, dtype=float)
    if pressure.shape != (n,) or not np.isfinite(pressure).all():
        raise ValueError("mode_pressure must match retained PCA component count")
    feature_loadings = loadings(result)
    weighted_modes = pressure * result.explained_variance_ratio_
    signed = feature_loadings @ weighted_modes
    absolute = np.abs(feature_loadings) @ np.abs(weighted_modes)
    if source_gap is None:
        gap = np.ones(len(result.feature_names_))
    else:
        gap = np.asarray(source_gap, dtype=float)
        if gap.shape != (len(result.feature_names_),) or not np.isfinite(gap).all():
            raise ValueError("source_gap must match feature count")
    source_weighted = absolute * gap
    records = [
        {
            "feature": name,
            "signed_contribution": float(signed[i]),
            "absolute_contribution": float(absolute[i]),
            "source_gap_contribution": float(source_weighted[i]),
        }
        for i, name in enumerate(result.feature_names_)
    ]
    records.sort(key=lambda row: row["source_gap_contribution"], reverse=True)
    return {
        "features": records,
        "mode_pressure": pressure.tolist(),
        "variance_weights": result.explained_variance_ratio_.tolist(),
        "authority": "NON_AUTHORITATIVE_DIAGNOSTIC",
        "guard": "not a BT weight and cannot override evidence or execution gates",
    }


def convergence_diagnostics(values: Iterable[float]) -> dict[str, Any]:
    """Classify an ordered scalar residual/metric history using transparent heuristics."""
    x = _finite_1d(values)
    if x.size < 4:
        return {"classification": "INSUFFICIENT_DATA", "sample_count": int(x.size)}
    idx = np.arange(x.size, dtype=float)
    slope = float(np.polyfit(idx, x, 1)[0])
    absx = np.abs(x)
    scale = max(float(absx.max()), np.finfo(float).eps)
    span = float(x.max() - x.min())
    tail = x[max(0, x.size // 2) :]
    tail_slope = float(np.polyfit(np.arange(tail.size, dtype=float), tail, 1)[0])
    nonzero_prev = np.maximum(absx[:-1], np.finfo(float).eps)
    ratios = absx[1:] / nonzero_prev
    median_ratio = float(np.median(ratios))
    alternating = bool(np.mean(np.signbit(x[1:]) != np.signbit(x[:-1])) >= 0.6)
    if span / scale < 0.02 and abs(slope) / scale < 0.005:
        classification = "STATIONARY"
    elif alternating and float(absx.max()) <= 1.2 * max(float(absx[0]), np.finfo(float).eps):
        classification = "OSCILLATORY_BOUNDED"
    elif median_ratio < 0.90 and absx[-1] < absx[0]:
        classification = "CONVERGING"
    elif median_ratio < 1.0 and absx[-1] < absx[0] and abs(tail_slope) < abs(slope):
        classification = "ASYMPTOTICALLY_CONVERGING"
    elif median_ratio > 1.05 and absx[-1] > absx[0]:
        classification = "DIVERGING"
    else:
        classification = "UNSTABLE"
    return {
        "classification": classification,
        "sample_count": int(x.size),
        "slope": slope,
        "tail_slope": tail_slope,
        "median_abs_successive_ratio": median_ratio,
        "initial_abs": float(absx[0]),
        "final_abs": float(absx[-1]),
        "alternating_sign": alternating,
        "authority": "DIAGNOSTIC_ONLY",
    }


def fourier_diagnostics(values: Iterable[float], *, sample_interval: float = 1.0) -> dict[str, Any]:
    """Real FFT/periodogram diagnostics for uniformly sampled observations."""
    x = _finite_1d(values)
    dt = float(sample_interval)
    if dt <= 0.0 or not np.isfinite(dt):
        raise ValueError("sample_interval must be finite and > 0")
    centered = x - x.mean()
    spectrum = np.fft.rfft(centered)
    frequencies = np.fft.rfftfreq(x.size, d=dt)
    power = (np.abs(spectrum) ** 2) / max(x.size, 1)
    if power.size > 1:
        dominant_index = 1 + int(np.argmax(power[1:]))
        dominant_frequency = float(frequencies[dominant_index])
    else:
        dominant_index, dominant_frequency = 0, 0.0
    return {
        "frequencies": frequencies.tolist(),
        "power": power.tolist(),
        "dominant_frequency": dominant_frequency,
        "dominant_period": (1.0 / dominant_frequency) if dominant_frequency > 0.0 else None,
        "nyquist_frequency": 1.0 / (2.0 * dt),
        "sample_interval": dt,
        "aliasing_warning": "frequencies above Nyquist cannot be observed and may alias",
        "authority": "DIAGNOSTIC_ONLY",
    }


def taylor_diagnostics(
    function: Any,
    point: Sequence[float],
    *,
    step: float = 1.0e-5,
    include_hessian: bool = True,
) -> dict[str, Any]:
    """Finite-difference local gradient/Hessian for an explicitly supplied callable."""
    x = _finite_1d(point, name="point")
    h = float(step)
    if h <= 0.0:
        raise ValueError("step must be > 0")
    f0 = float(function(x.copy()))
    grad = np.zeros_like(x)
    for i in range(x.size):
        e = np.zeros_like(x); e[i] = h
        grad[i] = (float(function(x + e)) - float(function(x - e))) / (2.0 * h)
    hessian = None
    if include_hessian:
        H = np.zeros((x.size, x.size))
        for i in range(x.size):
            ei = np.zeros_like(x); ei[i] = h
            H[i, i] = (float(function(x + ei)) - 2.0 * f0 + float(function(x - ei))) / (h * h)
            for j in range(i + 1, x.size):
                ej = np.zeros_like(x); ej[j] = h
                value = (
                    float(function(x + ei + ej)) - float(function(x + ei - ej))
                    - float(function(x - ei + ej)) + float(function(x - ei - ej))
                ) / (4.0 * h * h)
                H[i, j] = H[j, i] = value
        hessian = H.tolist()
    return {
        "point": x.tolist(),
        "value": f0,
        "gradient": grad.tolist(),
        "hessian": hessian,
        "approximation_order": 2,
        "step": h,
        "guard": "local finite-difference linearisation; validate the neighbourhood before extrapolation",
    }


def transfer_function_diagnostics(
    numerator: Sequence[float],
    denominator: Sequence[float],
    *,
    fast_time_constant: float | None = None,
    sluggish_time_constant: float | None = None,
) -> dict[str, Any]:
    """Continuous-time SISO transfer-function pole/zero and response diagnostics.

    Coefficients are descending powers of s.  The physical model structure and
    units must be supplied by the caller; this function never infers a transfer
    function from sparse KPI/project history.
    """
    num = _finite_1d(numerator, name="numerator")
    den = _finite_1d(denominator, name="denominator")
    num = np.trim_zeros(num, "f")
    den = np.trim_zeros(den, "f")
    if num.size == 0 or den.size < 2:
        raise ValueError("non-zero numerator and dynamic denominator are required")
    if num.size > den.size:
        raise ValueError("improper transfer functions are not supported")
    den = den / den[0]
    num = num / float(denominator[0])
    poles = np.roots(den)
    zeros = np.roots(num) if num.size > 1 else np.asarray([], dtype=complex)
    max_real = float(np.max(np.real(poles)))
    if max_real < -1.0e-10:
        stability = "STABLE"
    elif max_real > 1.0e-10:
        stability = "UNSTABLE"
    else:
        stability = "MARGINAL"
    dominant = poles[int(np.argmax(np.real(poles)))]
    time_constants = [float(-1.0 / p.real) for p in poles if p.real < -1.0e-12]
    damping = [float(-p.real / abs(p)) if abs(p) > 0 else None for p in poles]
    natural = [float(abs(p)) for p in poles]
    dc_gain = float(num[-1] / den[-1]) if abs(den[-1]) > np.finfo(float).eps else None
    dominant_tau = max(time_constants) if time_constants else None
    responsiveness = "NOT_EVALUATED"
    if dominant_tau is not None:
        if fast_time_constant is not None and dominant_tau <= fast_time_constant:
            responsiveness = "FAST"
        elif sluggish_time_constant is not None and dominant_tau >= sluggish_time_constant:
            responsiveness = "SLUGGISH"
        elif fast_time_constant is not None or sluggish_time_constant is not None:
            responsiveness = "ACCEPTABLE"
    return {
        "zeros": [[float(z.real), float(z.imag)] for z in zeros],
        "poles": [[float(p.real), float(p.imag)] for p in poles],
        "dominant_pole": [float(dominant.real), float(dominant.imag)],
        "time_constants": time_constants,
        "dominant_time_constant": dominant_tau,
        "damping_ratios": damping,
        "natural_frequencies": natural,
        "dc_gain": dc_gain,
        "stability_class": stability,
        "responsiveness_class": responsiveness,
        "guard": "declared model diagnostic only; not inferred from project KPI history",
    }


def closed_loop_transfer(
    forward_numerator: Sequence[float],
    forward_denominator: Sequence[float],
    *,
    feedback_numerator: Sequence[float] = (1.0,),
    feedback_denominator: Sequence[float] = (1.0,),
) -> dict[str, list[float]]:
    """Negative-feedback closed-loop G/(1+GH) polynomial coefficients."""
    ng = _finite_1d(forward_numerator, name="forward_numerator")
    dg = _finite_1d(forward_denominator, name="forward_denominator")
    nh = _finite_1d(feedback_numerator, name="feedback_numerator")
    dh = _finite_1d(feedback_denominator, name="feedback_denominator")
    numerator = np.polymul(ng, dh)
    denominator = np.polyadd(np.polymul(dg, dh), np.polymul(ng, nh))
    return {"numerator": numerator.tolist(), "denominator": denominator.tolist()}
