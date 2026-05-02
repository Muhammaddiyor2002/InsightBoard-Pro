"""Recommend the best chart types for a given dataframe profile."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class ChartSuggestion:
    """Suggestion to plot a particular chart with specific columns."""

    chart: str  # bar | line | pie | scatter | histogram | box | heatmap | timeseries
    columns: list[str]
    rationale: str
    score: float


class ChartRecommender:
    """Score and rank chart suggestions for *df*."""

    def suggest(self, df: pd.DataFrame, *, max_results: int = 6) -> list[ChartSuggestion]:
        if df.empty:
            return []
        suggestions: list[ChartSuggestion] = []
        numeric = df.select_dtypes(include=[np.number]).columns.tolist()
        date_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
        cat_cols = [
            c
            for c in df.columns
            if c not in numeric and c not in date_cols and 1 < df[c].nunique() <= 50
        ]

        # Time-series
        for d in date_cols:
            for n in numeric:
                suggestions.append(
                    ChartSuggestion(
                        "timeseries",
                        [d, n],
                        f"{n} over time ({d})",
                        score=0.95,
                    )
                )

        # Correlation
        if len(numeric) >= 2:
            suggestions.append(
                ChartSuggestion(
                    "correlation",
                    numeric[:6],
                    "Multiple numeric columns; correlation heatmap reveals relationships.",
                    score=0.9,
                )
            )
            suggestions.append(
                ChartSuggestion(
                    "scatter",
                    numeric[:2],
                    f"Scatter of {numeric[0]} vs {numeric[1]} to inspect correlation.",
                    score=0.7,
                )
            )

        # Bar / pie for categorical splits
        for c in cat_cols[:3]:
            for n in numeric[:1]:
                suggestions.append(
                    ChartSuggestion(
                        "bar",
                        [c, n],
                        f"Compare {n} across {c} categories.",
                        score=0.85,
                    )
                )
            uniq = df[c].nunique()
            if 2 <= uniq <= 6:
                suggestions.append(
                    ChartSuggestion(
                        "pie",
                        [c],
                        f"Share of rows by {c} (small cardinality {uniq}).",
                        score=0.6,
                    )
                )

        # Histogram for distributions
        for n in numeric[:3]:
            suggestions.append(
                ChartSuggestion(
                    "histogram",
                    [n],
                    f"Distribution of {n}.",
                    score=0.5,
                )
            )

        # Box plot for outlier-prone columns
        for n in numeric[:3]:
            suggestions.append(
                ChartSuggestion(
                    "box",
                    [n],
                    f"Spread and outliers of {n}.",
                    score=0.45,
                )
            )

        suggestions.sort(key=lambda s: s.score, reverse=True)
        # de-duplicate same chart-type w/ same columns
        seen: set[tuple[str, tuple[str, ...]]] = set()
        unique: list[ChartSuggestion] = []
        for s in suggestions:
            key = (s.chart, tuple(s.columns))
            if key in seen:
                continue
            seen.add(key)
            unique.append(s)
        return unique[:max_results]
