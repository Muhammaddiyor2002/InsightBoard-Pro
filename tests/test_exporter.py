"""Exporter tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.services.exporter import Exporter
from app.services.insights import Insight


def test_export_csv(sample_df: pd.DataFrame, tmp_path: Path) -> None:
    e = Exporter(tmp_path)
    p = e.export_csv(sample_df)
    assert p.exists()
    df = pd.read_csv(p)
    assert len(df) == len(sample_df)


def test_export_excel(sample_df: pd.DataFrame, tmp_path: Path) -> None:
    e = Exporter(tmp_path)
    p = e.export_excel(
        sample_df,
        extra_sheets={"summary": pd.DataFrame({"k": ["a"], "v": [1]})},
    )
    assert p.exists()


def test_export_text_summary(sample_df: pd.DataFrame, tmp_path: Path) -> None:
    e = Exporter(tmp_path)
    insights = [Insight("Top region", "North leads", "top", 0.9)]
    p = e.export_text_summary(sample_df, insights=insights)
    body = p.read_text()
    assert "InsightBoard Pro" in body
    assert "Top region" in body


def test_export_pdf(sample_df: pd.DataFrame, tmp_path: Path) -> None:
    e = Exporter(tmp_path)
    insights = [Insight("Trend", "rising", "trend", 0.7)]
    p = e.export_pdf_dashboard(sample_df, kpis={"rows": "10"}, insights=insights)
    assert p.exists()
    assert p.stat().st_size > 1000  # non-trivial PDF
