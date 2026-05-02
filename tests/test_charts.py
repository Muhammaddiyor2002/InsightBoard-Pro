"""Chart factory tests."""

from __future__ import annotations

import pandas as pd
import pytest

from app.charts import ChartFactory


@pytest.fixture
def factory() -> ChartFactory:
    return ChartFactory()


def test_bar_chart(factory: ChartFactory, sample_df: pd.DataFrame) -> None:
    fig = factory.build("bar", sample_df, x="region", y="revenue")
    assert len(fig.data) >= 1


def test_line_chart(factory: ChartFactory, sample_df: pd.DataFrame) -> None:
    fig = factory.build("line", sample_df, x="date", y="revenue")
    assert len(fig.data) >= 1


def test_pie_chart(factory: ChartFactory, sample_df: pd.DataFrame) -> None:
    fig = factory.build("pie", sample_df, names="region", values="revenue")
    assert len(fig.data) >= 1


def test_histogram(factory: ChartFactory, sample_df: pd.DataFrame) -> None:
    fig = factory.build("histogram", sample_df, x="price")
    assert len(fig.data) >= 1


def test_scatter(factory: ChartFactory, sample_df: pd.DataFrame) -> None:
    fig = factory.build("scatter", sample_df, x="units", y="price")
    assert len(fig.data) >= 1


def test_box(factory: ChartFactory, sample_df: pd.DataFrame) -> None:
    fig = factory.build("box", sample_df, y="price", x="region")
    assert len(fig.data) >= 1


def test_heatmap(factory: ChartFactory, sample_df: pd.DataFrame) -> None:
    fig = factory.build("heatmap", sample_df)
    assert len(fig.data) >= 1


def test_area(factory: ChartFactory, sample_df: pd.DataFrame) -> None:
    fig = factory.build("area", sample_df, x="date", y="revenue")
    assert len(fig.data) >= 1


def test_correlation(factory: ChartFactory, sample_df: pd.DataFrame) -> None:
    fig = factory.build("correlation", sample_df)
    assert len(fig.data) >= 1


def test_timeseries(factory: ChartFactory, sample_df: pd.DataFrame) -> None:
    fig = factory.build("timeseries", sample_df, x="date", y="revenue")
    assert len(fig.data) >= 1


def test_unknown_kind_raises(factory: ChartFactory, sample_df: pd.DataFrame) -> None:
    with pytest.raises(ValueError):
        factory.build("rainbow", sample_df)  # type: ignore[arg-type]


def test_empty_df_returns_placeholder(factory: ChartFactory) -> None:
    fig = factory.build("bar", pd.DataFrame(), x="a", y="b")
    # Empty placeholder figure has at least one annotation
    assert len(fig.layout.annotations) >= 1
