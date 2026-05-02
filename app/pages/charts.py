"""Charts page — pick chart type + columns and render."""

from __future__ import annotations

from typing import cast

import flet as ft
import numpy as np

from app.charts import ChartFactory
from app.charts.factory import ChartKind
from app.components.chart_card import ChartCard
from app.components.snackbar import Notifier
from app.pages._common import empty_state, page_header
from app.state import AppState
from app.ui.theme import AppTheme

CHART_OPTIONS = [
    ("bar", "Bar"),
    ("line", "Line"),
    ("pie", "Pie"),
    ("histogram", "Histogram"),
    ("scatter", "Scatter"),
    ("box", "Box"),
    ("heatmap", "Heatmap"),
    ("area", "Area"),
    ("correlation", "Correlation"),
    ("timeseries", "Time-series"),
]


class ChartsPage:
    def __init__(self, theme: AppTheme, state: AppState, notifier: Notifier) -> None:
        self.theme = theme
        self.state = state
        self.notifier = notifier
        self.factory = ChartFactory()
        self._chart_type = ft.Dropdown(
            label="Chart type",
            options=[ft.dropdown.Option(k, label=lbl) for k, lbl in CHART_OPTIONS],
            value="bar",
            on_change=self._render,
            border_color=self.theme.border,
            color=self.theme.text,
        )
        self._x = ft.Dropdown(
            label="X / dimension",
            on_change=self._render,
            border_color=self.theme.border,
            color=self.theme.text,
        )
        self._y = ft.Dropdown(
            label="Y / metric",
            on_change=self._render,
            border_color=self.theme.border,
            color=self.theme.text,
        )
        self._chart_host = ft.Container(expand=True)

    def build(self) -> ft.Control:
        if not self.state.has_data():
            return empty_state(self.theme, "No data", "Upload a file first.")
        df = self.state.df
        cols = [ft.dropdown.Option(c) for c in df.columns]
        numeric_cols = [
            ft.dropdown.Option(c) for c in df.select_dtypes(include=[np.number]).columns
        ]
        self._x.options = cols
        self._y.options = numeric_cols if numeric_cols else cols
        self._x.value = df.columns[0]
        self._y.value = (
            df.select_dtypes(include=[np.number]).columns[0]
            if df.select_dtypes(include=[np.number]).shape[1]
            else df.columns[0]
        )
        self._render(None)
        return ft.Column(
            controls=[
                page_header(
                    self.theme,
                    "Charts",
                    "Ten Plotly chart types — fully interactive in the desktop build.",
                ),
                ft.Row(
                    controls=[self._chart_type, self._x, self._y],
                    spacing=10,
                ),
                ft.Container(height=10),
                self._chart_host,
            ],
            expand=True,
            spacing=8,
        )

    def _render(self, _: ft.ControlEvent | None) -> None:
        kind: ChartKind = cast(ChartKind, self._chart_type.value or "bar")
        x = self._x.value
        y = self._y.value
        df = self.state.df
        kwargs: dict[str, object] = {}
        if kind in {"bar", "line", "scatter", "area", "timeseries"}:
            kwargs.update({"x": x, "y": y})
        elif kind == "pie":
            kwargs.update({"names": x, "values": y})
        elif kind == "histogram":
            kwargs.update({"x": y or x})
        elif kind == "box":
            kwargs.update({"x": x, "y": y})
        elif kind in {"heatmap", "correlation"}:
            kwargs.update({})
        figure = self.factory.build(kind, df, **kwargs)
        card = ChartCard(
            self.theme,
            title=f"{kind.title()} — {x} × {y}",
            figure=figure,
            on_export=self._export,
        ).build()
        self._chart_host.content = card
        if self._chart_host.page:
            self._chart_host.update()

    def _export(self, figure) -> None:
        try:
            path = self.state.exporter.export_chart_png(figure, "chart")
        except (RuntimeError, OSError) as exc:
            self.notifier.error(f"Export failed: {exc}")
            return
        self.notifier.success(f"Saved chart to {path}")
