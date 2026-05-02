"""Lazy-loading DataTable viewer for large pandas DataFrames."""

from __future__ import annotations

import flet as ft
import pandas as pd

from app.ui.theme import AppTheme


class DataTableViewer:
    """Render a pandas DataFrame as a paginated Flet DataTable."""

    def __init__(
        self,
        theme: AppTheme,
        *,
        df: pd.DataFrame,
        page_size: int = 25,
        max_rows_in_ui: int = 5000,
    ) -> None:
        self.theme = theme
        self.df = df.head(max_rows_in_ui)
        self.page_size = page_size
        self.page_index = 0

        self._table = ft.DataTable(
            columns=[],
            rows=[],
            heading_row_color=theme.surface,
            divider_thickness=0.5,
            column_spacing=18,
            data_row_max_height=42,
        )
        self._page_label = ft.Text("", color=theme.muted, size=12)

    @property
    def total_pages(self) -> int:
        if self.df.empty:
            return 1
        return max(1, (len(self.df) + self.page_size - 1) // self.page_size)

    def build(self) -> ft.Control:
        self._refresh()
        controls: list[ft.Control] = [
            ft.Row(
                controls=[
                    ft.Text(
                        f"{len(self.df):,} rows × {self.df.shape[1]} columns",
                        color=self.theme.muted,
                        size=12,
                    ),
                    ft.Container(expand=True),
                    ft.IconButton(
                        ft.Icons.CHEVRON_LEFT,
                        icon_color=self.theme.muted,
                        on_click=lambda _: self._navigate(-1),
                    ),
                    self._page_label,
                    ft.IconButton(
                        ft.Icons.CHEVRON_RIGHT,
                        icon_color=self.theme.muted,
                        on_click=lambda _: self._navigate(1),
                    ),
                ],
            ),
            ft.Container(
                content=ft.Column(
                    controls=[self._table],
                    scroll=ft.ScrollMode.AUTO,
                ),
                bgcolor=self.theme.surface,
                border=ft.border.all(1, self.theme.border),
                border_radius=12,
                padding=12,
                expand=True,
            ),
        ]
        return ft.Column(controls=controls, expand=True, spacing=10)

    # ------------------------------------------------------------------ #
    def _navigate(self, delta: int) -> None:
        self.page_index = max(0, min(self.total_pages - 1, self.page_index + delta))
        self._refresh()

    def _refresh(self) -> None:
        if self.df.empty:
            self._table.columns = [ft.DataColumn(ft.Text("No data", color=self.theme.muted))]
            self._table.rows = []
            self._page_label.value = "0 / 0"
            return

        self._table.columns = [
            ft.DataColumn(
                ft.Text(
                    str(c),
                    color=self.theme.text,
                    weight=ft.FontWeight.W_600,
                    size=12,
                )
            )
            for c in self.df.columns
        ]
        start = self.page_index * self.page_size
        chunk = self.df.iloc[start : start + self.page_size]
        rows: list[ft.DataRow] = []
        for _, row in chunk.iterrows():
            cells = [
                ft.DataCell(
                    ft.Text(
                        "" if pd.isna(v) else str(v),
                        color=self.theme.text,
                        size=12,
                    )
                )
                for v in row.tolist()
            ]
            rows.append(ft.DataRow(cells=cells))
        self._table.rows = rows
        self._page_label.value = f"{self.page_index + 1} / {self.total_pages}"
