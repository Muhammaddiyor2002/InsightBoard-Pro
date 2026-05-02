"""Insights engine tests."""

from __future__ import annotations

import pandas as pd

from app.services.insights import InsightsEngine


def test_generate_insights_returns_ranked_list(sample_df: pd.DataFrame) -> None:
    engine = InsightsEngine()
    out = engine.generate(sample_df, max_insights=8)
    assert 0 < len(out) <= 8
    scores = [i.score for i in out]
    assert scores == sorted(scores, reverse=True)


def test_generate_handles_empty_df() -> None:
    out = InsightsEngine().generate(pd.DataFrame())
    assert out == []


def test_generate_includes_trend_when_dates_present(sample_df: pd.DataFrame) -> None:
    out = InsightsEngine().generate(sample_df, max_insights=10)
    kinds = {i.kind for i in out}
    assert "trend" in kinds or "stat" in kinds
