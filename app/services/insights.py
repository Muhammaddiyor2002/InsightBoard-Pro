"""Auto-Insights engine — surfaces non-obvious facts about a dataset."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.utils.logger import get_logger

log = get_logger("insights")


@dataclass
class Insight:
    """A single auto-generated insight."""

    title: str
    detail: str
    kind: str  # "trend" | "spike" | "anomaly" | "top" | "stat"
    score: float = 0.0  # higher = more important

    def as_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "detail": self.detail,
            "kind": self.kind,
            "score": self.score,
        }


class InsightsEngine:
    """Generate a ranked list of insights from a dataframe."""

    def generate(self, df: pd.DataFrame, *, max_insights: int = 8) -> list[Insight]:
        if df.empty:
            return []
        insights: list[Insight] = []
        insights += list(self._top_categories(df))
        insights += list(self._numeric_extremes(df))
        insights += list(self._trend_insights(df))
        insights += list(self._anomaly_insights(df))
        insights.sort(key=lambda i: i.score, reverse=True)
        log.info("generated %d insights", len(insights))
        return insights[:max_insights]

    # ------------------------------------------------------------------ #
    def _top_categories(self, df: pd.DataFrame) -> Iterable[Insight]:
        cat_cols = [
            c
            for c in df.columns
            if (df[c].dtype == "object" or pd.api.types.is_string_dtype(df[c]))
            and 1 < df[c].nunique() <= 50
        ]
        for col in cat_cols[:3]:
            top = df[col].value_counts(dropna=True).head(1)
            if top.empty:
                continue
            label = top.index[0]
            count = int(top.iloc[0])
            share = count / max(1, len(df))
            yield Insight(
                title=f"Most common {col}: {label}",
                detail=(f"{count:,} rows ({share:.1%} of dataset). This is {col}'s mode."),
                kind="top",
                score=0.4 + share,
            )

    def _numeric_extremes(self, df: pd.DataFrame) -> Iterable[Insight]:
        numeric = df.select_dtypes(include=[np.number])
        for col in numeric.columns[:5]:
            s = numeric[col].dropna()
            if s.empty:
                continue
            mx, mn = float(s.max()), float(s.min())
            yield Insight(
                title=f"Range of {col}: {mn:,.2f} to {mx:,.2f}",
                detail=(
                    f"Mean {s.mean():,.2f}, median {s.median():,.2f}, std {s.std(ddof=0):,.2f}."
                ),
                kind="stat",
                score=0.3,
            )

    def _trend_insights(self, df: pd.DataFrame) -> Iterable[Insight]:
        date_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns
        numeric = df.select_dtypes(include=[np.number]).columns
        if len(date_cols) == 0 or len(numeric) == 0:
            return
        date_col = date_cols[0]
        for metric in numeric[:2]:
            grouped = (
                df.dropna(subset=[date_col])
                .assign(__d__=df[date_col].dt.to_period("M").astype(str))
                .groupby("__d__")[metric]
                .sum(min_count=1)
                .dropna()
            )
            if len(grouped) < 3:
                continue
            xs = np.arange(len(grouped))
            ys = grouped.to_numpy(dtype=float)
            slope = float(np.polyfit(xs, ys, 1)[0])
            direction = "upward" if slope > 0 else "downward"
            mag = abs(slope) / (np.mean(np.abs(ys)) + 1e-9)
            yield Insight(
                title=f"{direction.title()} trend in {metric}",
                detail=(
                    f"Across {len(grouped)} months, {metric} shows a "
                    f"{direction} slope of {slope:,.2f} per period."
                ),
                kind="trend",
                score=0.6 + min(0.4, mag),
            )

    def _anomaly_insights(self, df: pd.DataFrame) -> Iterable[Insight]:
        numeric = df.select_dtypes(include=[np.number])
        for col in numeric.columns[:3]:
            s = numeric[col].dropna()
            if len(s) < 10:
                continue
            q1, q3 = np.quantile(s, [0.25, 0.75])
            iqr = q3 - q1
            if iqr <= 0:
                continue
            outliers = s[(s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)]
            if outliers.empty:
                continue
            share = len(outliers) / len(s)
            yield Insight(
                title=f"{len(outliers)} outliers detected in {col}",
                detail=(
                    f"{share:.1%} of values fall outside the IQR fence "
                    f"[{q1 - 1.5 * iqr:,.2f}, {q3 + 1.5 * iqr:,.2f}]."
                ),
                kind="anomaly",
                score=0.5 + min(0.4, share * 4),
            )
