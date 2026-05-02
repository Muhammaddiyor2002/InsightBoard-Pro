"""Export center component — buttons that drive the Exporter service."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.ui.theme import AppTheme


class ExportCenter:
    """Card listing all export actions."""

    def __init__(
        self,
        theme: AppTheme,
        *,
        on_export_csv: Callable[[], None],
        on_export_excel: Callable[[], None],
        on_export_pdf: Callable[[], None],
        on_export_summary: Callable[[], None],
    ) -> None:
        self.theme = theme
        self.on_export_csv = on_export_csv
        self.on_export_excel = on_export_excel
        self.on_export_pdf = on_export_pdf
        self.on_export_summary = on_export_summary

    def build(self) -> ft.Control:
        def tile(icon: str, title: str, sub: str, action: Callable[[], None]) -> ft.Control:
            return ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Icon(icon, color="white", size=20),
                            bgcolor=self.theme.primary,
                            padding=10,
                            border_radius=10,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(title, color=self.theme.text, weight=ft.FontWeight.W_600),
                                ft.Text(sub, color=self.theme.muted, size=11),
                            ],
                            spacing=2,
                        ),
                        ft.Container(expand=True),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT, color=self.theme.muted),
                    ],
                    spacing=12,
                ),
                padding=14,
                border=ft.border.all(1, self.theme.border),
                border_radius=12,
                bgcolor=self.theme.surface,
                on_click=lambda _: action(),
                ink=True,
            )

        return ft.Column(
            controls=[
                tile(
                    ft.Icons.TABLE_VIEW,
                    "Export cleaned CSV",
                    "Filtered, cleaned dataframe as CSV.",
                    self.on_export_csv,
                ),
                tile(
                    ft.Icons.GRID_ON,
                    "Export Excel report",
                    "Multi-sheet workbook (data, profile, KPIs).",
                    self.on_export_excel,
                ),
                tile(
                    ft.Icons.PICTURE_AS_PDF,
                    "Export PDF dashboard",
                    "Snapshot of KPIs and Auto-Insights.",
                    self.on_export_pdf,
                ),
                tile(
                    ft.Icons.NOTES,
                    "Export text summary",
                    "Plain-text overview of the dataset.",
                    self.on_export_summary,
                ),
            ],
            spacing=10,
        )
