"""Data cleaner tests."""

from __future__ import annotations

import numpy as np
import pandas as pd

from app.services.data_cleaner import DataCleaner


def test_clean_drops_duplicates() -> None:
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    cleaned, report = DataCleaner().clean(df)
    assert report.duplicates_removed == 1
    assert len(cleaned) == 2


def test_clean_fills_numeric_median(sample_df: pd.DataFrame) -> None:
    cleaned, report = DataCleaner(numeric_fill="median").clean(sample_df)
    assert cleaned["price"].isna().sum() == 0
    assert report.missing_filled > 0


def test_clean_drops_empty_columns() -> None:
    df = pd.DataFrame({"a": [1, 2, 3], "b": [None, None, None]})
    cleaned, report = DataCleaner().clean(df)
    assert "b" not in cleaned.columns
    assert "b" in report.empty_columns_dropped


def test_clean_flags_outliers() -> None:
    df = pd.DataFrame({"v": [1, 2, 3, 4, 5, 6, 7, 8, 9, 1000]})
    cleaned, report = DataCleaner().clean(df)
    assert report.outliers_flagged >= 1
    assert "__outlier__" in cleaned.columns


def test_profile_returns_per_column_rows() -> None:
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", None, "y"]})
    profile = DataCleaner.profile(df)
    assert set(profile["column"]) == {"a", "b"}
    assert profile.loc[profile["column"] == "b", "nulls"].iloc[0] == 1


def test_clean_detects_dates() -> None:
    df = pd.DataFrame({"d": ["2024-01-01", "2024-01-02", "2024-01-03"], "x": [1, 2, 3]})
    cleaned, report = DataCleaner().clean(df)
    assert pd.api.types.is_datetime64_any_dtype(cleaned["d"])
    assert "d" in report.columns_converted


def test_clean_keeps_dtype_when_no_change() -> None:
    df = pd.DataFrame({"x": np.arange(10)})
    cleaned, _ = DataCleaner().clean(df)
    assert pd.api.types.is_integer_dtype(cleaned["x"])
