"""File loader tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.services.file_loader import FileLoader


def test_load_csv(sample_csv: Path) -> None:
    loader = FileLoader()
    ds = loader.load(sample_csv)
    assert ds.rows > 0
    assert ds.cols >= 5
    assert "date" in ds.df.columns
    assert ds.delimiter == ","


def test_load_xlsx(sample_xlsx: Path) -> None:
    loader = FileLoader()
    ds = loader.load(sample_xlsx)
    assert ds.rows > 0
    assert ds.sheet_name is not None


def test_load_rejects_unknown_extension(tmp_path: Path) -> None:
    p = tmp_path / "bad.bin"
    p.write_bytes(b"\x00\x01")
    loader = FileLoader()
    with pytest.raises(ValueError):
        loader.load(p)


def test_load_rejects_oversize(tmp_path: Path) -> None:
    p = tmp_path / "huge.csv"
    p.write_text("a,b\n1,2\n")
    loader = FileLoader(max_size_mb=0)  # forces failure
    with pytest.raises(ValueError):
        loader.load(p)


def test_load_with_semicolon_delim(tmp_path: Path) -> None:
    p = tmp_path / "semi.csv"
    p.write_text("a;b;c\n1;2;3\n4;5;6\n")
    ds = FileLoader().load(p)
    assert list(ds.df.columns) == ["a", "b", "c"]
    assert len(ds.df) == 2


def test_post_process_parses_iso_dates(tmp_path: Path) -> None:
    p = tmp_path / "dates.csv"
    p.write_text(
        "name,event\nalpha,2024-01-15\nbeta,2024-02-20\ngamma,2024-03-08\ndelta,2024-04-12\n"
    )
    ds = FileLoader().load(p)
    import pandas as _pd

    assert _pd.api.types.is_datetime64_any_dtype(ds.df["event"])


def test_post_process_strips_whitespace(tmp_path: Path) -> None:
    p = tmp_path / "ws.csv"
    p.write_text(" col_a , col_b \n hello , 1 \n world , 2 \n")
    ds = FileLoader().load(p)
    assert list(ds.df.columns) == ["col_a", "col_b"]
    assert ds.df["col_a"].iloc[0] == "hello"
