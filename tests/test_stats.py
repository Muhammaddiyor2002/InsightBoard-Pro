"""Stats helper tests."""

from __future__ import annotations

import pandas as pd

from app.analytics.stats import correlation_matrix, describe_dataframe, kpi_summary


def test_kpi_summary_empty() -> None:
    out = kpi_summary(pd.DataFrame())
    assert out["rows"] == 0


def test_kpi_summary_counts(sample_df: pd.DataFrame) -> None:
    out = kpi_summary(sample_df)
    assert out["rows"] == len(sample_df)
    assert out["numeric_columns"] >= 3
    assert out["date_columns"] >= 1


def test_describe_returns_dataframe(sample_df: pd.DataFrame) -> None:
    desc = describe_dataframe(sample_df)
    assert not desc.empty


def test_correlation_matrix(sample_df: pd.DataFrame) -> None:
    corr = correlation_matrix(sample_df)
    assert corr.shape[0] == corr.shape[1]
    assert corr.shape[0] >= 2
