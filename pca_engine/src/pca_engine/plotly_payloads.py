"""Plotly-ready, dependency-free JSON payload builders.

These functions return plain dictionaries compatible with Plotly's figure JSON
shape.  Plotly itself is intentionally not a runtime dependency of the engine.
"""
from __future__ import annotations

from typing import Any, Iterable, Sequence

import numpy as np

from .pca_core import PCAResult
from .pca_loadings import loadings


def _list(values: Iterable[float]) -> list[float]:
    return [float(v) for v in values]


def metric_history_payload(
    x: Sequence[Any],
    values: Sequence[float],
    *,
    ci_lower: Sequence[float] | None = None,
    ci_upper: Sequence[float] | None = None,
    baseline_mean: float | None = None,
    baseline_std: float | None = None,
    sigma_levels: Sequence[float] = (3.0, 4.0, 5.0, 6.0),
    title: str = "Metric history",
) -> dict[str, Any]:
    if len(x) != len(values):
        raise ValueError("x and values must have equal length")
    traces: list[dict[str, Any]] = [{"type": "scatter", "mode": "lines+markers", "name": "observed", "x": list(x), "y": _list(values)}]
    if ci_lower is not None or ci_upper is not None:
        if ci_lower is None or ci_upper is None or len(ci_lower) != len(x) or len(ci_upper) != len(x):
            raise ValueError("both CI bounds must match x length")
        traces.extend([
            {"type": "scatter", "mode": "lines", "name": "CI upper", "x": list(x), "y": _list(ci_upper), "line": {"width": 0}, "showlegend": False},
            {"type": "scatter", "mode": "lines", "name": "95% CI", "x": list(x), "y": _list(ci_lower), "fill": "tonexty", "line": {"width": 0}},
        ])
    shapes: list[dict[str, Any]] = []
    if baseline_mean is not None and baseline_std is not None:
        for level in sigma_levels:
            for sign in (-1.0, 1.0):
                y = float(baseline_mean + sign * float(level) * baseline_std)
                shapes.append({"type": "line", "xref": "paper", "x0": 0, "x1": 1, "y0": y, "y1": y, "line": {"dash": "dot"}, "name": f"{sign * level:+g} sigma"})
    return {"data": traces, "layout": {"title": title, "xaxis": {"title": "Wave / time"}, "yaxis": {"title": "Metric"}, "shapes": shapes}, "authority": "OBSERVATION_SURFACE_ONLY"}


def covariance_heatmap_payload(matrix: Sequence[Sequence[float]], labels: Sequence[str], *, title: str = "Covariance matrix") -> dict[str, Any]:
    z = np.asarray(matrix, dtype=float)
    if z.ndim != 2 or z.shape[0] != z.shape[1] or z.shape[0] != len(labels):
        raise ValueError("matrix must be square and match labels")
    return {"data": [{"type": "heatmap", "z": z.tolist(), "x": list(labels), "y": list(labels), "colorbar": {"title": "Value"}}], "layout": {"title": title}, "authority": "OBSERVATION_SURFACE_ONLY"}


def pca_scree_payload(result: PCAResult) -> dict[str, Any]:
    pcs = list(range(1, result.n_components_ + 1))
    return {"data": [{"type": "bar", "name": "Explained variance", "x": pcs, "y": result.explained_variance_ratio_.tolist()}], "layout": {"title": "PCA scree", "xaxis": {"title": "Principal component"}, "yaxis": {"title": "Explained variance ratio"}}, "authority": "OBSERVATION_SURFACE_ONLY"}


def pca_loadings_payload(result: PCAResult, *, component: int = 0) -> dict[str, Any]:
    if not 0 <= component < result.n_components_:
        raise ValueError("component out of range")
    vals = loadings(result)[:, component]
    return {"data": [{"type": "bar", "x": list(result.feature_names_), "y": vals.tolist(), "name": f"PC{component + 1}"}], "layout": {"title": f"PC{component + 1} loadings", "yaxis": {"title": "Loading"}}, "authority": "OBSERVATION_SURFACE_ONLY"}


def eigen_spectrum_payload(eigenvalues: Sequence[float], *, title: str = "Eigenvalue spectrum") -> dict[str, Any]:
    vals = _list(eigenvalues)
    return {"data": [{"type": "scatter", "mode": "lines+markers", "x": list(range(1, len(vals) + 1)), "y": vals, "name": "eigenvalue"}], "layout": {"title": title, "xaxis": {"title": "Mode"}, "yaxis": {"title": "Eigenvalue"}}, "authority": "OBSERVATION_SURFACE_ONLY"}


def reverse_pressure_payload(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    names = [str(r["feature"]) for r in records]
    signed = [float(r["signed_contribution"]) for r in records]
    gap = [float(r.get("source_gap_contribution", abs(signed[i]))) for i, r in enumerate(records)]
    return {"data": [
        {"type": "bar", "name": "signed contribution", "x": names, "y": signed},
        {"type": "bar", "name": "source-gap pressure", "x": names, "y": gap},
    ], "layout": {"title": "Reverse pressure by source metric", "barmode": "group", "yaxis": {"title": "Diagnostic pressure"}}, "authority": "NON_AUTHORITATIVE_DIAGNOSTIC"}


def frequency_spectrum_payload(frequencies: Sequence[float], power: Sequence[float]) -> dict[str, Any]:
    if len(frequencies) != len(power):
        raise ValueError("frequencies and power must have equal length")
    return {"data": [{"type": "scatter", "mode": "lines", "x": _list(frequencies), "y": _list(power), "name": "power"}], "layout": {"title": "Frequency spectrum", "xaxis": {"title": "Frequency"}, "yaxis": {"title": "Power"}}, "authority": "OBSERVATION_SURFACE_ONLY"}


def time_response_payload(time: Sequence[float], response: Sequence[float], *, reference: Sequence[float] | None = None) -> dict[str, Any]:
    if len(time) != len(response):
        raise ValueError("time and response must have equal length")
    data: list[dict[str, Any]] = [{"type": "scatter", "mode": "lines", "x": _list(time), "y": _list(response), "name": "response"}]
    if reference is not None:
        if len(reference) != len(time):
            raise ValueError("reference must match time length")
        data.append({"type": "scatter", "mode": "lines", "x": _list(time), "y": _list(reference), "name": "reference", "line": {"dash": "dash"}})
    return {"data": data, "layout": {"title": "Declared dynamic-model response", "xaxis": {"title": "Time"}, "yaxis": {"title": "Response"}}, "authority": "DECLARED_MODEL_DIAGNOSTIC_ONLY"}
