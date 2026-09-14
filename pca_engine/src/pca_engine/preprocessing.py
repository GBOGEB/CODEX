"""Numeric selection, missing-value handling, centering and scaling."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class PreprocessResult:
    input_matrix: np.ndarray
    matrix: np.ndarray
    feature_names: list[str]
    mean: np.ndarray
    scale: np.ndarray
    imputation_values: np.ndarray
    center: bool
    scaled: bool


def _numeric_frame(data: Any) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        frame = data.select_dtypes(include=[np.number]).copy()
        if frame.shape[1] == 0:
            raise ValueError("no numeric columns found")
        return frame
    arr = np.asarray(data, dtype=float)
    if arr.ndim != 2:
        raise ValueError("data must be a 2D table")
    return pd.DataFrame(arr, columns=[f"x{i}" for i in range(arr.shape[1])])


def prepare_numeric(
    data: Any,
    *,
    missing: str = "mean",
    center: bool = True,
    scale: bool = True,
) -> PreprocessResult:
    """Prepare a numeric matrix while preserving reusable feature metadata.

    missing: one of ``mean``, ``median``, ``zero``, ``drop``, or ``error``.
    Constant columns receive scale=1 to avoid division by zero.
    """
    frame = _numeric_frame(data)
    names = [str(c) for c in frame.columns]

    if missing == "error" and frame.isna().any().any():
        raise ValueError("missing values present")
    if missing == "drop":
        frame = frame.dropna(axis=0)
        fill = np.full(frame.shape[1], np.nan)
    elif missing == "zero":
        fill = np.zeros(frame.shape[1], dtype=float)
        frame = frame.fillna(dict(zip(frame.columns, fill)))
    elif missing in {"mean", "median"}:
        stats = frame.mean() if missing == "mean" else frame.median()
        if stats.isna().any():
            raise ValueError("a numeric column contains only missing values")
        fill = stats.to_numpy(dtype=float)
        frame = frame.fillna(stats)
    elif missing != "error":
        raise ValueError(f"unsupported missing policy: {missing}")
    else:
        fill = np.full(frame.shape[1], np.nan)

    raw = frame.to_numpy(dtype=float)
    if raw.shape[0] < 2:
        raise ValueError("at least two rows are required")
    mean = raw.mean(axis=0)
    centered = raw - mean if center else raw.copy()
    std = raw.std(axis=0, ddof=1)
    safe_scale = np.where(std == 0.0, 1.0, std)
    matrix = centered / safe_scale if scale else centered

    return PreprocessResult(
        input_matrix=raw,
        matrix=matrix,
        feature_names=names,
        mean=mean,
        scale=safe_scale if scale else np.ones_like(safe_scale),
        imputation_values=fill,
        center=center,
        scaled=scale,
    )
