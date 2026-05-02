"""Sidebar navigation component."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import flet as ft

from app.ui.theme import AppTheme


@dataclass
class SidebarItem:
    key: str
    label: str
    icon: str


class Sidebar:
    """Vertical sidebar with navigation, theme toggle and footer."""

    def __init__(
        self,
        *,
        items: list[SidebarItem],
        theme: AppTheme,
        on_select: Callable[[str], None],
        on_theme_toggle: Callable[[], None],
        width: int = 240,
    ) -> None:
        self.items = items
        self.theme = theme
        self.on_select = on_select
        self.on_theme_toggle = on_theme_toggle
        self.width = width
        self.active = items[0].key if items else ""

        self._buttons: dict[str, ft.Container] = {}
        self._container: ft.Container | None = None

    # ------------------------------------------------------------------ #
    def build(self) -> ft.Control:
        header = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(ft.Icons.INSIGHTS, color="white", size=22),
                    bgcolor=self.theme.primary,
                    padding=8,
                    border_radius=10,
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            "InsightBoard",
                            color=self.theme.text,
                            weight=ft.FontWeight.BOLD,
                            size=16,
                        ),
                        ft.Text("Pro · v1.0", color=self.theme.muted, size=11),
                    ],
                    spacing=0,
                ),
            ],
            spacing=10,
        )

        nav_buttons = []
        for item in self.items:
            btn = self._build_button(item)
            self._buttons[item.key] = btn
            nav_buttons.append(btn)

        nav = ft.Column(controls=nav_buttons, spacing=4, expand=True)

        footer = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.DARK_MODE if self.theme.is_dark else ft.Icons.LIGHT_MODE,
                                color=self.theme.muted,
                                size=18,
                            ),
                            ft.Text(
                                "Toggle theme",
                                color=self.theme.muted,
                                size=12,
                            ),
                        ],
                        spacing=10,
                    ),
                    on_click=lambda _: self.on_theme_toggle(),
                    padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    border_radius=10,
                    ink=True,
                ),
                ft.Text(
                    "© 2026 Cognition Labs",
                    size=10,
                    color=self.theme.muted,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            spacing=4,
        )

        column = ft.Column(
            controls=[
                ft.Container(content=header, padding=ft.padding.only(left=16, top=20, bottom=20)),
                ft.Divider(color=self.theme.border, height=1),
                ft.Container(
                    content=nav,
                    padding=ft.padding.symmetric(horizontal=10, vertical=10),
                    expand=True,
                ),
                ft.Divider(color=self.theme.border, height=1),
                ft.Container(
                    content=footer, padding=ft.padding.symmetric(horizontal=10, vertical=12)
                ),
            ],
            spacing=0,
            expand=True,
        )

        self._container = ft.Container(
            content=column,
            width=self.width,
            bgcolor=self.theme.surface,
            border=ft.border.only(right=ft.BorderSide(1, self.theme.border)),
        )
        return self._container

    # ------------------------------------------------------------------ #
    def _build_button(self, item: SidebarItem) -> ft.Container:
        is_active = item.key == self.active
        return ft.Container(
            data=item.key,
            content=ft.Row(
                controls=[
                    ft.Icon(item.icon, size=18, color=self._icon_color(is_active)),
                    ft.Text(item.label, size=13, color=self._text_color(is_active)),
                ],
                spacing=12,
            ),
            padding=ft.padding.symmetric(horizontal=14, vertical=10),
            bgcolor=self._bg_color(is_active),
            border_radius=10,
            on_click=lambda e: self.on_select(e.control.data),
            ink=True,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
        )

    def _bg_color(self, active: bool) -> str | None:
        return f"{self.theme.primary}33" if active else None

    def _text_color(self, active: bool) -> str:
        return self.theme.text if active else self.theme.muted

    def _icon_color(self, active: bool) -> str:
        return self.theme.primary if active else self.theme.muted

    # ------------------------------------------------------------------ #
    def set_active(self, route: str) -> None:
        self.active = route
        for key, btn in self._buttons.items():
            is_active = key == route
            btn.bgcolor = self._bg_color(is_active)
            row: ft.Row = btn.content
            icon: ft.Icon = row.controls[0]
            text: ft.Text = row.controls[1]
            icon.color = self._icon_color(is_active)
            text.color = self._text_color(is_active)

    def refresh(self) -> None:
        """Re-apply theme colours after a theme change."""
        if self._container:
            self._container.bgcolor = self.theme.surface
            self._container.border = ft.border.only(right=ft.BorderSide(1, self.theme.border))
        self.set_active(self.active)
