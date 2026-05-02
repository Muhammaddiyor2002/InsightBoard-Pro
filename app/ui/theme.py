"""Centralised theme tokens used by every component."""

from __future__ import annotations

from dataclasses import dataclass, field

import flet as ft


@dataclass
class AppTheme:
    """Design tokens for InsightBoard Pro."""

    mode: str = "dark"  # "dark" | "light"

    primary: str = "#7C3AED"
    accent: str = "#06B6D4"
    success: str = "#22C55E"
    warning: str = "#F59E0B"
    danger: str = "#EF4444"

    bg_dark: str = "#0F172A"
    surface_dark: str = "#1E293B"
    border_dark: str = "#334155"
    text_dark: str = "#E2E8F0"
    muted_dark: str = "#94A3B8"

    bg_light: str = "#F8FAFC"
    surface_light: str = "#FFFFFF"
    border_light: str = "#E2E8F0"
    text_light: str = "#0F172A"
    muted_light: str = "#475569"

    palette: tuple[str, ...] = field(
        default_factory=lambda: (
            "#7C3AED",
            "#06B6D4",
            "#22C55E",
            "#F59E0B",
            "#EF4444",
            "#3B82F6",
            "#EC4899",
            "#10B981",
        )
    )

    # ------------------------------------------------------------------ #
    @property
    def is_dark(self) -> bool:
        return self.mode == "dark"

    @property
    def bg(self) -> str:
        return self.bg_dark if self.is_dark else self.bg_light

    @property
    def surface(self) -> str:
        return self.surface_dark if self.is_dark else self.surface_light

    @property
    def border(self) -> str:
        return self.border_dark if self.is_dark else self.border_light

    @property
    def text(self) -> str:
        return self.text_dark if self.is_dark else self.text_light

    @property
    def muted(self) -> str:
        return self.muted_dark if self.is_dark else self.muted_light

    def toggle(self) -> None:
        self.mode = "light" if self.is_dark else "dark"

    def apply(self, page: ft.Page) -> None:
        """Push theme tokens to the given Flet ``page``."""
        page.theme_mode = ft.ThemeMode.DARK if self.is_dark else ft.ThemeMode.LIGHT
        page.bgcolor = self.bg
        page.theme = ft.Theme(
            color_scheme_seed=self.primary,
            font_family="Inter",
            visual_density=ft.VisualDensity.COMFORTABLE,
        )
        page.update()
