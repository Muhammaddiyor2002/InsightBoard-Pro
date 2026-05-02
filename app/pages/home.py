"""Home / landing page."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.pages._common import page_header
from app.ui.theme import AppTheme


class HomePage:
    """Welcome page with quick links."""

    def __init__(
        self,
        theme: AppTheme,
        *,
        on_navigate: Callable[[str], None],
        version: str,
    ) -> None:
        self.theme = theme
        self.on_navigate = on_navigate
        self.version = version

    def build(self) -> ft.Control:
        cards = [
            self._card(
                "Upload data",
                "Bring in CSV / Excel and start exploring",
                ft.Icons.CLOUD_UPLOAD,
                "upload",
            ),
            self._card(
                "Open dashboard",
                "KPI cards, auto-insights, recommendations",
                ft.Icons.DASHBOARD,
                "dashboard",
            ),
            self._card(
                "Build charts",
                "Ten interactive Plotly chart types",
                ft.Icons.SHOW_CHART,
                "charts",
            ),
            self._card(
                "Export reports",
                "PDF, Excel, CSV, plain-text summaries",
                ft.Icons.SAVE_ALT,
                "reports",
            ),
        ]
        return ft.Column(
            controls=[
                page_header(
                    self.theme,
                    "Welcome to InsightBoard Pro",
                    f"Premium analytics, version {self.version}",
                ),
                ft.Container(height=10),
                ft.GridView(
                    controls=cards,
                    runs_count=2,
                    max_extent=320,
                    child_aspect_ratio=2.4,
                    spacing=14,
                    run_spacing=14,
                    expand=True,
                ),
            ],
            expand=True,
            spacing=10,
        )

    def _card(self, title: str, sub: str, icon: str, route: str) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(icon, color="white", size=22),
                        bgcolor=self.theme.primary,
                        padding=12,
                        border_radius=10,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(title, color=self.theme.text, weight=ft.FontWeight.W_600),
                            ft.Text(sub, color=self.theme.muted, size=11),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Icon(ft.Icons.ARROW_FORWARD, color=self.theme.muted),
                ],
                spacing=14,
            ),
            on_click=lambda _: self.on_navigate(route),
            padding=18,
            bgcolor=self.theme.surface,
            border=ft.border.all(1, self.theme.border),
            border_radius=14,
            ink=True,
        )
