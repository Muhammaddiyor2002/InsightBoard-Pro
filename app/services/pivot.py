"""Group-by / aggregation helper used by the Pivot Analytics page."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

import pandas as pd

AggKind = Literal["sum", "mean", "median", "count", "min", "max"]
_FUNC_MAP: dict[AggKind, str] = {
    "sum": "sum",
    "mean": "mean",
    "median": "median",
    "count": "count",
    "min": "min",
    "max": "max",
}


class Aggregator:
    """Build group-by summaries for arbitrary column / metric combinations."""

    def aggregate(
        self,
        df: pd.DataFrame,
        *,
        group_by: Iterable[str],
        metric: str,
        how: AggKind = "sum",
    ) -> pd.DataFrame:
        """Group *df* by *group_by* and aggregate *metric* using *how*."""
        gb = list(group_by)
        if not gb:
            raise ValueError("group_by must contain at least one column")
        if metric not in df.columns:
            raise ValueError(f"metric column not found: {metric}")
        if how not in _FUNC_MAP:
            raise ValueError(f"unsupported aggregation: {how}")

        if how == "count":
            out = df.groupby(gb, dropna=False)[metric].count().reset_index()
        else:
            series = pd.to_numeric(df[metric], errors="coerce")
            out = (
                df.assign(__metric__=series)
                .groupby(gb, dropna=False)["__metric__"]
                .agg(_FUNC_MAP[how])
                .reset_index()
                .rename(columns={"__metric__": metric})
            )
        return out.sort_values(metric, ascending=False, na_position="last")

    def crosstab(
        self,
        df: pd.DataFrame,
        *,
        rows: str,
        cols: str,
        metric: str,
        how: AggKind = "sum",
    ) -> pd.DataFrame:
        """Build a 2D pivot table (rows × cols) of *metric*."""
        if how == "count":
            return pd.crosstab(df[rows], df[cols], values=df[metric], aggfunc="count").fillna(0)
        return df.pivot_table(
            index=rows,
            columns=cols,
            values=metric,
            aggfunc=_FUNC_MAP[how],
            fill_value=0,
        )
