"""Outlier detection tests."""

from __future__ import annotations

import pandas as pd

from app.analytics.outliers import detect_outliers


def test_iqr_flags_extreme() -> None:
    s = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1000])
    mask = detect_outliers(s, method="iqr")
    assert mask.iloc[-1]


def test_zscore() -> None:
    s = pd.Series([1, 2, 3, 4, 5, 100])
    mask = detect_outliers(s, method="zscore", z_thresh=2.0)
    assert mask.iloc[-1]


def test_handles_non_numeric() -> None:
    s = pd.Series(["a", "b", "c"])
    mask = detect_outliers(s)
    assert not mask.any()


def test_handles_zero_iqr() -> None:
    s = pd.Series([5, 5, 5, 5])
    mask = detect_outliers(s)
    assert not mask.any()
