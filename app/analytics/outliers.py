"""Outlier detection helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd


def detect_outliers(
    series: pd.Series, *, method: str = "iqr", iqr_mult: float = 1.5, z_thresh: float = 3.0
) -> pd.Series:
    """Return a boolean Series flagging outliers in *series*.

    Two methods are supported:

    - ``"iqr"`` (default) — Tukey fence at ``iqr_mult * IQR`` from Q1/Q3.
    - ``"zscore"`` — flag values whose absolute z-score exceeds ``z_thresh``.
    """
    if not pd.api.types.is_numeric_dtype(series):
        return pd.Series(False, index=series.index)
    s = series.astype(float)
    if method == "zscore":
        std = s.std(ddof=0)
        if std == 0 or np.isnan(std):
            return pd.Series(False, index=series.index)
        z = (s - s.mean()) / std
        return z.abs() > z_thresh
    # IQR
    q1, q3 = s.quantile([0.25, 0.75])
    iqr = q3 - q1
    if iqr == 0 or np.isnan(iqr):
        return pd.Series(False, index=series.index)
    lo = q1 - iqr_mult * iqr
    hi = q3 + iqr_mult * iqr
    return (s < lo) | (s > hi)
