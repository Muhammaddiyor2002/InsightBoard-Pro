"""Compact KPI card component."""

from __future__ import annotations

import flet as ft

from app.ui.theme import AppTheme


class KpiCard:
    """A premium KPI card with title, big value, optional sub-label."""

    def __init__(
        self,
        theme: AppTheme,
        *,
        title: str,
        value: str,
        sub: str = "",
        icon: str = ft.Icons.SHOW_CHART,
        accent: str | None = None,
    ) -> None:
        self.theme = theme
        self.title = title
        self.value = value
        self.sub = sub
        self.icon = icon
        self.accent = accent or theme.primary

    def build(self) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(self.icon, color="white", size=18),
                                bgcolor=self.accent,
                                padding=8,
                                border_radius=8,
                            ),
                            ft.Text(
                                self.title.upper(),
                                color=self.theme.muted,
                                weight=ft.FontWeight.W_500,
                                size=11,
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Text(
                        self.value,
                        color=self.theme.text,
                        size=26,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(self.sub, color=self.theme.muted, size=11),
                ],
                spacing=6,
            ),
            bgcolor=self.theme.surface,
            border=ft.border.all(1, self.theme.border),
            border_radius=14,
            padding=16,
            expand=True,
            shadow=ft.BoxShadow(
                blur_radius=18,
                spread_radius=0,
                color="#00000022" if self.theme.is_dark else "#00000010",
                offset=ft.Offset(0, 4),
            ),
        )
