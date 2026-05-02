"""Chart recommender tests."""

from __future__ import annotations

import pandas as pd

from app.analytics.recommender import ChartRecommender


def test_recommends_for_sample_df(sample_df: pd.DataFrame) -> None:
    suggestions = ChartRecommender().suggest(sample_df, max_results=5)
    assert 1 <= len(suggestions) <= 5
    kinds = {s.chart for s in suggestions}
    # Has timeseries because we have a date + numeric
    assert "timeseries" in kinds or "correlation" in kinds


def test_handles_empty() -> None:
    assert ChartRecommender().suggest(pd.DataFrame()) == []
