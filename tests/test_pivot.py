"""Aggregator (pivot) tests."""

from __future__ import annotations

import pandas as pd
import pytest

from app.services.pivot import Aggregator


def test_aggregate_sum(sample_df: pd.DataFrame) -> None:
    out = Aggregator().aggregate(sample_df, group_by=["region"], metric="revenue", how="sum")
    assert set(out["region"]) <= {"North", "South", "East", "West"}
    assert (out["revenue"] >= 0).all()


def test_aggregate_count(sample_df: pd.DataFrame) -> None:
    out = Aggregator().aggregate(sample_df, group_by=["region"], metric="revenue", how="count")
    assert out["revenue"].sum() == len(sample_df)


def test_aggregate_invalid_metric(sample_df: pd.DataFrame) -> None:
    with pytest.raises(ValueError):
        Aggregator().aggregate(sample_df, group_by=["region"], metric="missing", how="sum")


def test_aggregate_no_group_by(sample_df: pd.DataFrame) -> None:
    with pytest.raises(ValueError):
        Aggregator().aggregate(sample_df, group_by=[], metric="revenue", how="sum")


def test_aggregate_unknown_func(sample_df: pd.DataFrame) -> None:
    with pytest.raises(ValueError):
        Aggregator().aggregate(sample_df, group_by=["region"], metric="revenue", how="banana")  # type: ignore[arg-type]


def test_crosstab_creates_pivot(sample_df: pd.DataFrame) -> None:
    out = Aggregator().crosstab(
        sample_df, rows="region", cols="category", metric="revenue", how="sum"
    )
    assert out.shape[0] >= 1 and out.shape[1] >= 1
