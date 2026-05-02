"""Lightweight notification helper."""

from __future__ import annotations

import flet as ft

from app.ui.theme import AppTheme


class Notifier:
    """Display Snack-bar style notifications via the page overlay."""

    def __init__(self, page: ft.Page, theme: AppTheme) -> None:
        self.page = page
        self.theme = theme

    def info(self, message: str) -> None:
        self._show(message, self.theme.primary)

    def success(self, message: str) -> None:
        self._show(message, self.theme.success)

    def warn(self, message: str) -> None:
        self._show(message, self.theme.warning)

    def error(self, message: str) -> None:
        self._show(message, self.theme.danger)

    # ------------------------------------------------------------------ #
    def _show(self, message: str, color: str) -> None:
        snack = ft.SnackBar(
            content=ft.Text(message, color="white"),
            bgcolor=color,
            behavior=ft.SnackBarBehavior.FLOATING,
            shape=ft.RoundedRectangleBorder(radius=10),
        )
        self.page.open(snack)
