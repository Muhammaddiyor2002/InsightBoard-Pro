"""High-level chart factory backed by Plotly Express / Graph Objects."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

ChartKind = Literal[
    "bar",
    "line",
    "pie",
    "histogram",
    "scatter",
    "box",
    "heatmap",
    "area",
    "correlation",
    "timeseries",
]


@dataclass
class ChartTheme:
    """Visual configuration applied to every figure."""

    template: str = "plotly_dark"
    primary: str = "#7C3AED"
    accent: str = "#06B6D4"
    palette: tuple[str, ...] = (
        "#7C3AED",
        "#06B6D4",
        "#22C55E",
        "#F59E0B",
        "#EF4444",
        "#3B82F6",
        "#EC4899",
        "#10B981",
    )
    font_family: str = "Inter, system-ui, sans-serif"


class ChartFactory:
    """Factory for the ten supported chart types."""

    def __init__(self, theme: ChartTheme | None = None) -> None:
        self.theme = theme or ChartTheme()

    # ------------------------------------------------------------------ #
    # Public dispatcher                                                   #
    # ------------------------------------------------------------------ #
    def build(self, kind: ChartKind, df: pd.DataFrame, **kwargs: object) -> go.Figure:
        if df.empty:
            return self._empty("No data to visualise")
        method = getattr(self, kind, None)
        if method is None:
            raise ValueError(f"Unknown chart kind: {kind}")
        try:
            fig = method(df, **kwargs)
        except (KeyError, ValueError, TypeError) as exc:
            return self._empty(f"Cannot render: {exc}")
        return self._style(fig)

    # ------------------------------------------------------------------ #
    # Individual chart builders                                           #
    # ------------------------------------------------------------------ #
    def bar(
        self,
        df: pd.DataFrame,
        *,
        x: str,
        y: str,
        color: str | None = None,
        agg: str = "sum",
        top_n: int = 25,
    ) -> go.Figure:
        grouped = self._group(df, x, y, agg).head(top_n)
        return px.bar(
            grouped,
            x=x,
            y=y,
            color=color if color and color in df.columns else None,
            color_discrete_sequence=list(self.theme.palette),
        )

    def line(
        self,
        df: pd.DataFrame,
        *,
        x: str,
        y: str,
        color: str | None = None,
    ) -> go.Figure:
        d = df.sort_values(x)
        return px.line(
            d,
            x=x,
            y=y,
            color=color if color and color in df.columns else None,
            color_discrete_sequence=list(self.theme.palette),
        )

    def pie(self, df: pd.DataFrame, *, names: str, values: str | None = None) -> go.Figure:
        if values and values in df.columns:
            data = df.groupby(names, dropna=False)[values].sum().reset_index()
            return px.pie(
                data,
                names=names,
                values=values,
                color_discrete_sequence=list(self.theme.palette),
            )
        counts = df[names].value_counts().reset_index()
        counts.columns = [names, "count"]
        return px.pie(
            counts,
            names=names,
            values="count",
            color_discrete_sequence=list(self.theme.palette),
        )

    def histogram(self, df: pd.DataFrame, *, x: str, bins: int = 30) -> go.Figure:
        return px.histogram(
            df,
            x=x,
            nbins=bins,
            color_discrete_sequence=[self.theme.primary],
        )

    def scatter(
        self,
        df: pd.DataFrame,
        *,
        x: str,
        y: str,
        color: str | None = None,
        size: str | None = None,
    ) -> go.Figure:
        return px.scatter(
            df,
            x=x,
            y=y,
            color=color if color and color in df.columns else None,
            size=size if size and size in df.columns else None,
            color_discrete_sequence=list(self.theme.palette),
            opacity=0.85,
        )

    def box(self, df: pd.DataFrame, *, y: str, x: str | None = None) -> go.Figure:
        return px.box(
            df,
            x=x if x and x in df.columns else None,
            y=y,
            color_discrete_sequence=list(self.theme.palette),
        )

    def heatmap(self, df: pd.DataFrame, *, columns: Iterable[str] | None = None) -> go.Figure:
        cols = list(columns) if columns else df.select_dtypes(include=np.number).columns.tolist()
        if len(cols) < 2:
            return self._empty("Need at least two numeric columns for a heatmap")
        corr = df[cols].corr(numeric_only=True)
        return px.imshow(
            corr,
            color_continuous_scale="Tealrose",
            aspect="auto",
            zmin=-1,
            zmax=1,
        )

    def area(self, df: pd.DataFrame, *, x: str, y: str, color: str | None = None) -> go.Figure:
        d = df.sort_values(x)
        return px.area(
            d,
            x=x,
            y=y,
            color=color if color and color in df.columns else None,
            color_discrete_sequence=list(self.theme.palette),
        )

    def correlation(self, df: pd.DataFrame) -> go.Figure:
        return self.heatmap(df)

    def timeseries(
        self,
        df: pd.DataFrame,
        *,
        x: str,
        y: str,
        agg: str = "sum",
        freq: str = "ME",
    ) -> go.Figure:
        d = df.dropna(subset=[x]).copy()
        d[x] = pd.to_datetime(d[x], errors="coerce")
        d = d.dropna(subset=[x])
        if d.empty:
            return self._empty("No valid dates")
        d = d.set_index(x).sort_index()
        if pd.api.types.is_numeric_dtype(d[y]):
            grouped = d[y].resample(freq).agg(agg)
        else:
            grouped = d[y].resample(freq).count()
        out = grouped.reset_index().rename(columns={x: "date", y: y})
        return px.line(
            out,
            x="date",
            y=y,
            color_discrete_sequence=[self.theme.primary],
            markers=True,
        )

    # ------------------------------------------------------------------ #
    # Helpers                                                             #
    # ------------------------------------------------------------------ #
    def _group(self, df: pd.DataFrame, x: str, y: str, agg: str) -> pd.DataFrame:
        if x not in df.columns or y not in df.columns:
            return df
        if not pd.api.types.is_numeric_dtype(df[y]) and agg != "count":
            agg = "count"
        if agg == "count":
            return (
                df.groupby(x, dropna=False)[y].count().reset_index().sort_values(y, ascending=False)
            )
        return df.groupby(x, dropna=False)[y].agg(agg).reset_index().sort_values(y, ascending=False)

    def _style(self, fig: go.Figure) -> go.Figure:
        fig.update_layout(
            template=self.theme.template,
            font={"family": self.theme.font_family, "size": 12},
            margin={"l": 40, "r": 20, "t": 50, "b": 40},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend={"bgcolor": "rgba(0,0,0,0)"},
            hoverlabel={"font_family": self.theme.font_family},
        )
        return fig

    def _empty(self, message: str) -> go.Figure:
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font={"size": 14, "color": "#9CA3AF"},
        )
        return self._style(fig)
