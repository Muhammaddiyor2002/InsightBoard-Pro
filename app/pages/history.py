"""History page — recent uploads, saved filters, dashboard templates."""

from __future__ import annotations

import flet as ft

from app.pages._common import page_header
from app.state import AppState
from app.ui.theme import AppTheme


class HistoryPage:
    def __init__(self, theme: AppTheme, state: AppState) -> None:
        self.theme = theme
        self.state = state

    def build(self) -> ft.Control:
        files = self.state.files_repo.list(limit=20)
        filters = self.state.filters_repo.list()
        templates = self.state.templates_repo.list()
        exports = self.state.export_log_repo.list(limit=20)

        def section(title: str, items: list[ft.Control]) -> ft.Control:
            return ft.Column(
                controls=[
                    ft.Text(
                        title,
                        color=self.theme.text,
                        weight=ft.FontWeight.BOLD,
                        size=14,
                    ),
                    *items,
                ],
                spacing=6,
            )

        return ft.Column(
            controls=[
                page_header(self.theme, "History", "Recent uploads, filters and exports."),
                ft.Container(height=10),
                section(
                    "Uploaded files",
                    [self._file_row(f) for f in files]
                    or [ft.Text("None yet.", color=self.theme.muted, size=11)],
                ),
                ft.Container(height=12),
                section(
                    "Saved filters",
                    [ft.Text(f"• {f.name}", color=self.theme.text, size=12) for f in filters]
                    or [ft.Text("None yet.", color=self.theme.muted, size=11)],
                ),
                ft.Container(height=12),
                section(
                    "Dashboard templates",
                    [ft.Text(f"• {t.name}", color=self.theme.text, size=12) for t in templates]
                    or [ft.Text("None yet.", color=self.theme.muted, size=11)],
                ),
                ft.Container(height=12),
                section(
                    "Recent exports",
                    [
                        ft.Text(
                            f"• [{e.kind.upper()}] {e.path}",
                            color=self.theme.text,
                            size=12,
                        )
                        for e in exports
                    ]
                    or [ft.Text("None yet.", color=self.theme.muted, size=11)],
                ),
            ],
            expand=True,
            spacing=6,
            scroll=ft.ScrollMode.AUTO,
        )

    def _file_row(self, f) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.TABLE_VIEW, color=self.theme.muted),
                    ft.Column(
                        controls=[
                            ft.Text(f.filename, color=self.theme.text, weight=ft.FontWeight.W_500),
                            ft.Text(
                                f"{f.rows or '?'} rows × {f.cols or '?'} cols  •  {f.created_at}",
                                color=self.theme.muted,
                                size=11,
                            ),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=10,
            ),
            bgcolor=self.theme.surface,
            border=ft.border.all(1, self.theme.border),
            border_radius=10,
            padding=12,
        )
