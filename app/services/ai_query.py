"""Lightweight, rule-based natural-language query parser.

The architecture is *AI-ready*: drop in a real LLM by replacing
:meth:`AIQueryService._intent_from_text` with a structured-output prompt.
For now we keep dependencies minimal by using a regex grammar that
covers the most common analytical questions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

import pandas as pd

ChartKind = Literal["bar", "line", "pie", "histogram", "scatter", "table"]
AggKind = Literal["sum", "mean", "median", "count", "min", "max"]


@dataclass
class QueryIntent:
    """Structured representation of a natural-language query."""

    chart: ChartKind
    metric: str | None
    dimension: str | None
    aggregation: AggKind = "sum"
    filter_text: str | None = None
    raw: str = ""

    def as_dict(self) -> dict[str, object]:
        return {
            "chart": self.chart,
            "metric": self.metric,
            "dimension": self.dimension,
            "aggregation": self.aggregation,
            "filter_text": self.filter_text,
            "raw": self.raw,
        }


_CHART_HINTS: dict[ChartKind, tuple[str, ...]] = {
    "bar": ("bar", "compare", "ranking"),
    "line": ("line", "trend", "over time", "by month", "by year", "by week"),
    "pie": ("pie", "share", "distribution of"),
    "histogram": ("histogram", "distribution"),
    "scatter": ("scatter", "vs", "versus", "correlation between"),
    "table": ("table", "show me", "list"),
}

_AGG_HINTS: dict[AggKind, tuple[str, ...]] = {
    "sum": ("total", "sum", "sum of"),
    "mean": ("average", "avg", "mean"),
    "median": ("median",),
    "count": ("count", "how many", "number of"),
    "min": ("minimum", "min"),
    "max": ("maximum", "max"),
}


class AIQueryService:
    """Parse natural-language analytical queries into structured intents."""

    def parse(self, text: str, df: pd.DataFrame) -> QueryIntent:
        text = (text or "").strip()
        return self._intent_from_text(text, df)

    # ------------------------------------------------------------------ #
    def _intent_from_text(self, text: str, df: pd.DataFrame) -> QueryIntent:
        lowered = text.lower()
        chart: ChartKind = self._infer_chart(lowered)
        agg: AggKind = self._infer_agg(lowered)
        cols = list(df.columns)
        metric = self._first_match(lowered, cols, prefer_numeric=df)
        dimension = self._first_match(
            lowered, [c for c in cols if c != metric], prefer_numeric=None
        )
        filt = self._extract_filter(lowered)
        return QueryIntent(
            chart=chart,
            metric=metric,
            dimension=dimension,
            aggregation=agg,
            filter_text=filt,
            raw=text,
        )

    @staticmethod
    def _infer_chart(text: str) -> ChartKind:
        for kind, hints in _CHART_HINTS.items():
            for h in hints:
                if h in text:
                    return kind
        return "bar"

    @staticmethod
    def _infer_agg(text: str) -> AggKind:
        for kind, hints in _AGG_HINTS.items():
            for h in hints:
                if h in text:
                    return kind
        return "sum"

    @staticmethod
    def _first_match(
        text: str, columns: list[str], *, prefer_numeric: pd.DataFrame | None
    ) -> str | None:
        # exact-substring match (case insensitive)
        for col in sorted(columns, key=len, reverse=True):
            if col.lower() in text:
                return col
        # numeric fallback
        if prefer_numeric is not None:
            numeric = prefer_numeric.select_dtypes(include="number").columns.tolist()
            if numeric:
                return numeric[0]
        return columns[0] if columns else None

    @staticmethod
    def _extract_filter(text: str) -> str | None:
        m = re.search(r"where (.+)", text)
        return m.group(1).strip() if m else None
