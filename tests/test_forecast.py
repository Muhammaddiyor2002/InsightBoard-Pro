"""Forecasting tests."""

from __future__ import annotations

import numpy as np
import pandas as pd

from app.analytics.forecast import forecast_series


def test_linear_forecast_extends_trend() -> None:
    idx = pd.date_range("2024-01-01", periods=24, freq="MS")
    s = pd.Series(np.arange(24, dtype=float), index=idx)
    out = forecast_series(s, periods=3, method="linear")
    assert len(out) == 3
    assert out["yhat"].iloc[-1] >= out["yhat"].iloc[0]


def test_seasonal_naive_repeats_period() -> None:
    s = pd.Series(np.tile([1, 2, 3, 4], 3), dtype=float)
    out = forecast_series(s, periods=4, method="seasonal_naive", season=4)
    assert len(out) == 4


def test_moving_average_returns_constant() -> None:
    s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    out = forecast_series(s, periods=3, method="moving_average", window=3)
    assert (out["yhat"] == out["yhat"].iloc[0]).all()


def test_empty_series_returns_empty() -> None:
    out = forecast_series(pd.Series([], dtype=float), periods=5)
    assert out.empty
