"""Filters page — multi-column filtering with live data table preview."""

from __future__ import annotations

import flet as ft

from app.components.data_table import DataTableViewer
from app.components.filter_panel import FilterPanel
from app.pages._common import empty_state, page_header
from app.services.filters import Filter
from app.state import AppState
from app.ui.theme import AppTheme


class FiltersPage:
    def __init__(self, theme: AppTheme, state: AppState) -> None:
        self.theme = theme
        self.state = state
        self._results_host = ft.Container(expand=True)
        self._summary = ft.Text(color=self.theme.muted, size=12)

    def build(self) -> ft.Control:
        if not self.state.has_data():
            return empty_state(self.theme, "No data", "Upload a file first.")
        df = self.state.cleaned
        assert df is not None
        panel = FilterPanel(self.theme, df=df, on_change=self._on_change)
        self._refresh(self.state.cleaned)
        return ft.Column(
            controls=[
                page_header(
                    self.theme,
                    "Filters",
                    "Compose multi-column filters — charts and exports update live.",
                ),
                ft.Row(
                    controls=[
                        panel.build(),
                        ft.Container(
                            content=ft.Column(
                                controls=[self._summary, self._results_host],
                                spacing=8,
                                expand=True,
                            ),
                            expand=True,
                            padding=ft.padding.only(left=14),
                        ),
                    ],
                    expand=True,
                    spacing=14,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
            expand=True,
            spacing=10,
        )

    def _on_change(self, flt: Filter) -> None:
        df = self.state.cleaned
        if df is None:
            return
        filtered = self.state.filter_engine.apply(df, flt)
        self.state.filtered = filtered
        self._refresh(filtered)

    def _refresh(self, df) -> None:
        if df is None:
            return
        self._summary.value = f"Filtered: {len(df):,} of {len(self.state.cleaned or []):,} rows"
        viewer = DataTableViewer(self.theme, df=df.head(self.state.config.max_table_rows_in_ui))
        self._results_host.content = viewer.build()
        if self._results_host.page:
            self._summary.update()
            self._results_host.update()
