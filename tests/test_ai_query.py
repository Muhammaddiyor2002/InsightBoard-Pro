"""AI query parser tests."""

from __future__ import annotations

import pandas as pd

from app.services.ai_query import AIQueryService


def test_parse_basic_bar(sample_df: pd.DataFrame) -> None:
    svc = AIQueryService()
    intent = svc.parse("Show total revenue by region", sample_df)
    assert intent.chart == "bar"
    assert intent.aggregation == "sum"
    assert intent.metric in {"revenue", "units", "price"}
    assert intent.dimension == "region"


def test_parse_line_trend(sample_df: pd.DataFrame) -> None:
    intent = AIQueryService().parse("Plot revenue trend over time", sample_df)
    assert intent.chart == "line"


def test_parse_pie_share(sample_df: pd.DataFrame) -> None:
    intent = AIQueryService().parse("share of revenue by region", sample_df)
    assert intent.chart == "pie"


def test_parse_extracts_filter(sample_df: pd.DataFrame) -> None:
    intent = AIQueryService().parse(
        "Show average price by category where region is north",
        sample_df,
    )
    assert intent.aggregation == "mean"
    assert intent.filter_text and "north" in intent.filter_text


def test_parse_handles_unknown_columns() -> None:
    df = pd.DataFrame({"x": [1, 2, 3]})
    intent = AIQueryService().parse("show me a histogram", df)
    assert intent.chart == "histogram"
    assert intent.metric == "x"
