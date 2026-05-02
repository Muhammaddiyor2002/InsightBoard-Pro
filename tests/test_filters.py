"""Filter engine tests."""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from app.services.filters import Filter, FilterEngine, NumericRange


def test_filter_categorical(sample_df: pd.DataFrame) -> None:
    flt = Filter(categorical={"region": ["North"]})
    out = FilterEngine().apply(sample_df, flt)
    assert (out["region"] == "North").all()


def test_filter_numeric_range(sample_df: pd.DataFrame) -> None:
    flt = Filter(numeric_ranges=[NumericRange("units", minimum=10, maximum=20)])
    out = FilterEngine().apply(sample_df, flt)
    assert out["units"].between(10, 20).all()


def test_filter_date_range(sample_df: pd.DataFrame) -> None:
    flt = Filter(
        date_column="date",
        date_from=datetime(2024, 2, 1),
        date_to=datetime(2024, 3, 1),
    )
    out = FilterEngine().apply(sample_df, flt)
    assert out["date"].min() >= pd.Timestamp("2024-02-01")
    assert out["date"].max() <= pd.Timestamp("2024-03-01")


def test_filter_text_search(sample_df: pd.DataFrame) -> None:
    flt = Filter(text_search="Books", text_columns=["category"])
    out = FilterEngine().apply(sample_df, flt)
    assert (out["category"].str.contains("Books", case=False, na=False)).all()


def test_filter_serialization_roundtrip() -> None:
    flt = Filter(
        text_search="abc",
        categorical={"region": ["South"]},
        numeric_ranges=[NumericRange("price", 1.0, 10.0)],
        date_column="date",
        date_from=datetime(2024, 1, 1),
    )
    payload = flt.to_dict()
    restored = Filter.from_dict(payload)
    assert restored.text_search == "abc"
    assert restored.categorical == {"region": ["South"]}
    assert restored.numeric_ranges[0].column == "price"
    assert restored.date_from == datetime(2024, 1, 1)


def test_filter_engine_no_op_for_empty_filter(sample_df: pd.DataFrame) -> None:
    out = FilterEngine().apply(sample_df, Filter())
    assert len(out) == len(sample_df)


def test_filter_text_search_works_with_string_dtype() -> None:
    """Text search should find matches in StringDtype columns, not just object dtype."""
    df = pd.DataFrame(
        {
            "name": pd.array(["Alice", "Bob", "alibaba"], dtype="string"),
            "value": [1, 2, 3],
        }
    )
    out = FilterEngine().apply(df, Filter(text_search="ali"))
    assert len(out) == 2
    assert set(out["name"]) == {"Alice", "alibaba"}
