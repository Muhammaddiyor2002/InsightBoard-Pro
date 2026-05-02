"""Standalone theme switcher (used on the Settings page)."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.ui.theme import AppTheme


class ThemeSwitcher:
    """Switch between dark and light mode."""

    def __init__(self, theme: AppTheme, on_toggle: Callable[[], None]) -> None:
        self.theme = theme
        self.on_toggle = on_toggle

    def build(self) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.DARK_MODE if self.theme.is_dark else ft.Icons.LIGHT_MODE,
                        color=self.theme.text,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text("Theme", color=self.theme.text, weight=ft.FontWeight.W_500),
                            ft.Text(
                                f"Currently {self.theme.mode}",
                                color=self.theme.muted,
                                size=11,
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.Switch(
                        value=self.theme.is_dark,
                        active_color=self.theme.primary,
                        on_change=lambda _: self.on_toggle(),
                    ),
                ],
            ),
            bgcolor=self.theme.surface,
            border=ft.border.all(1, self.theme.border),
            border_radius=12,
            padding=14,
        )
