"""Validator + formatter + encoding tests."""

from __future__ import annotations

from pathlib import Path

from app.utils.encoding import detect_delimiter, detect_encoding
from app.utils.formatters import human_bytes, human_number, percent
from app.utils.validators import sanitize_column_name, validate_file


def test_validate_missing_file(tmp_path: Path) -> None:
    res = validate_file(tmp_path / "missing.csv")
    assert not res.ok


def test_validate_extension(tmp_path: Path) -> None:
    p = tmp_path / "f.bin"
    p.write_text("x")
    res = validate_file(p)
    assert not res.ok


def test_validate_empty(tmp_path: Path) -> None:
    p = tmp_path / "f.csv"
    p.write_text("")
    res = validate_file(p)
    assert not res.ok


def test_validate_ok(tmp_path: Path) -> None:
    p = tmp_path / "f.csv"
    p.write_text("a,b\n1,2\n")
    res = validate_file(p)
    assert res.ok


def test_human_number() -> None:
    assert human_number(0) == "0"
    assert human_number(1234) == "1.2K"
    assert human_number(1_500_000) == "1.5M"
    assert human_number(-2_500_000_000) == "-2.5B"


def test_human_bytes() -> None:
    assert human_bytes(0) == "0 B"
    assert human_bytes(1024).endswith("KB")
    assert human_bytes(1024 * 1024).endswith("MB")


def test_percent() -> None:
    assert percent(1, 4) == "25.0%"
    assert percent(0, 0) == "0%"


def test_detect_encoding_and_delimiter(tmp_path: Path) -> None:
    p = tmp_path / "x.csv"
    p.write_text("a,b,c\n1,2,3\n4,5,6\n", encoding="utf-8")
    enc = detect_encoding(p)
    assert enc.lower() in {"utf-8", "ascii"}
    assert detect_delimiter(p, encoding=enc) == ","


def test_sanitize_column_name() -> None:
    assert sanitize_column_name("Hello World!") == "Hello World_"
    assert sanitize_column_name("") == "column"
    assert sanitize_column_name("col@name#1") == "col_name_1"
    assert sanitize_column_name("   ") == "column"
