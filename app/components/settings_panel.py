"""Settings panel component used by the Settings page."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.config import AppConfig
from app.ui.theme import AppTheme


class SettingsPanel:
    """A rich editor for runtime preferences."""

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
        items = [
            self._row(
                "Theme", f"{self.theme.mode.title()} mode", action=("Toggle", self.on_theme_toggle)
            ),
            self._row("Database", str(self.config.db_path)),
            self._row("Exports folder", str(self.config.exports_dir)),
            self._row("Max upload size", f"{self.config.max_file_size_mb} MB"),
            self._row("Allowed extensions", ", ".join(self.config.allowed_extensions)),
            self._row("Use DuckDB", "Yes" if self.config.use_duckdb else "No"),
            self._row("Chart point limit", f"{self.config.chart_max_points:,}"),
        ]
        return ft.Column(controls=items, spacing=8)

    def _row(
        self,
        title: str,
        value: str,
        *,
        action: tuple[str, Callable[[], None]] | None = None,
    ) -> ft.Control:
        controls: list[ft.Control] = [
            ft.Column(
                controls=[
                    ft.Text(title, color=self.theme.text, weight=ft.FontWeight.W_500),
                    ft.Text(value, color=self.theme.muted, size=11, no_wrap=False),
                ],
                spacing=2,
                expand=True,
            ),
        ]
        if action:
            label, cb = action
            controls.append(ft.OutlinedButton(label, on_click=lambda _: cb()))
        return ft.Container(
            content=ft.Row(controls=controls, spacing=12),
            bgcolor=self.theme.surface,
            border=ft.border.all(1, self.theme.border),
            border_radius=12,
            padding=14,
        )
