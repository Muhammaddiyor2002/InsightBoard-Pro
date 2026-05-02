"""Settings page."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.components.settings_panel import SettingsPanel
from app.config import AppConfig
from app.pages._common import page_header
from app.ui.theme import AppTheme


class SettingsPage:
    def __init__(
        self,
        theme: AppTheme,
        config: AppConfig,
        *,
        on_theme_toggle: Callable[[], None],
    ) -> None:
        self.theme = theme
        self.config = config
        self.on_theme_toggle = on_theme_toggle

    def build(self) -> ft.Control:
        panel = SettingsPanel(self.theme, self.config, on_theme_toggle=self.on_theme_toggle)
        return ft.Column(
            controls=[
                page_header(self.theme, "Settings", "Runtime preferences and paths."),
                ft.Container(height=10),
                panel.build(),
            ],
            expand=True,
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )
