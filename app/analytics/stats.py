"""Descriptive-statistics helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd


def kpi_summary(df: pd.DataFrame) -> dict[str, int | str]:
    """Compute the KPI cards used by the dashboard overview."""
    if df is None or df.empty:
        return {
            "rows": 0,
            "columns": 0,
            "missing_values": 0,
            "duplicate_rows": 0,
            "numeric_columns": 0,
            "categorical_columns": 0,
            "date_columns": 0,
            "memory_mb": "0.0 MB",
        }
    numeric = df.select_dtypes(include=[np.number]).shape[1]
    dates = df.select_dtypes(include=["datetime", "datetimetz"]).shape[1]
    categorical = df.shape[1] - numeric - dates
    mem_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    return {
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_columns": int(numeric),
        "categorical_columns": int(max(0, categorical)),
        "date_columns": int(dates),
        "memory_mb": f"{mem_mb:.2f} MB",
    }


def describe_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Return a wide describe() including object columns."""
    if df.empty:
        return pd.DataFrame()
    try:
        return df.describe(include="all", datetime_is_numeric=True).transpose()
    except TypeError:
        return df.describe(include="all").transpose()


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Return the Pearson correlation matrix for numeric columns."""
    numeric = df.select_dtypes(include=[np.number])
    if numeric.shape[1] < 2:
        return pd.DataFrame()
    return numeric.corr(numeric_only=True)
