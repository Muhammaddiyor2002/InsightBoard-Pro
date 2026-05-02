"""Lightweight time-series forecasting (naive linear / seasonal-naive)."""

from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd

ForecastMethod = Literal["linear", "seasonal_naive", "moving_average"]


def forecast_series(
    series: pd.Series,
    *,
    periods: int = 12,
    method: ForecastMethod = "linear",
    season: int = 12,
    window: int = 7,
) -> pd.DataFrame:
    """Forecast *periods* future steps for an indexed numeric ``series``.

    Returns a dataframe with columns ``["ds", "yhat", "yhat_lower", "yhat_upper"]``.
    """
    s = series.dropna().astype(float)
    if s.empty:
        return pd.DataFrame(columns=["ds", "yhat", "yhat_lower", "yhat_upper"])

    if not isinstance(s.index, pd.DatetimeIndex):
        s.index = pd.RangeIndex(len(s))

    if method == "linear":
        yhat = _linear_forecast(s, periods)
    elif method == "seasonal_naive":
        yhat = _seasonal_naive(s, periods, season)
    elif method == "moving_average":
        yhat = _moving_average(s, periods, window)
    else:  # pragma: no cover
        raise ValueError(f"unknown method: {method}")

    sigma = float(s.std(ddof=0))
    upper = yhat + 1.96 * sigma
    lower = yhat - 1.96 * sigma
    if isinstance(s.index, pd.DatetimeIndex):
        freq = pd.infer_freq(s.index) or "D"
        future_index = pd.date_range(s.index[-1], periods=periods + 1, freq=freq)[1:]
    else:
        future_index = pd.RangeIndex(
            start=int(s.index[-1]) + 1, stop=int(s.index[-1]) + 1 + periods
        )
    return pd.DataFrame(
        {
            "ds": future_index,
            "yhat": yhat,
            "yhat_lower": lower,
            "yhat_upper": upper,
        }
    )


def _linear_forecast(s: pd.Series, periods: int) -> np.ndarray:
    xs = np.arange(len(s))
    coef = np.polyfit(xs, s.to_numpy(), 1)
    future = np.arange(len(s), len(s) + periods)
    return coef[0] * future + coef[1]


def _seasonal_naive(s: pd.Series, periods: int, season: int) -> np.ndarray:
    if len(s) < season:
        return np.repeat(s.iloc[-1], periods)
    last_season = s.tail(season).to_numpy()
    reps = int(np.ceil(periods / season))
    return np.tile(last_season, reps)[:periods]


def _moving_average(s: pd.Series, periods: int, window: int) -> np.ndarray:
    w = max(1, min(window, len(s)))
    return np.repeat(s.tail(w).mean(), periods)
