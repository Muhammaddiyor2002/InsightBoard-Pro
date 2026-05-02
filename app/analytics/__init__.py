"""Pure-Python analytics helpers (no Flet dependency)."""

from app.analytics.forecast import forecast_series
from app.analytics.outliers import detect_outliers
from app.analytics.recommender import ChartRecommender, ChartSuggestion
from app.analytics.stats import describe_dataframe, kpi_summary

__all__ = [
    "ChartRecommender",
    "ChartSuggestion",
    "describe_dataframe",
    "detect_outliers",
    "forecast_series",
    "kpi_summary",
]
