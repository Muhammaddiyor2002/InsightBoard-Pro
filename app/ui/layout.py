"""Top-level application shell: sidebar + content area."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.components.sidebar import Sidebar, SidebarItem
from app.ui.router import Router
from app.ui.theme import AppTheme


class AppLayout:
    """Stitches the sidebar to a content area driven by the router."""

    def __init__(
        self,
        page: ft.Page,
        theme: AppTheme,
        router: Router,
        items: list[SidebarItem],
        on_theme_toggle: Callable[[], None],
    ) -> None:
        self.page = page
        self.theme = theme
        self.router = router
        self.items = items
        self.on_theme_toggle = on_theme_toggle

        self.content = ft.Container(expand=True, padding=24)
        self.sidebar = Sidebar(
            items=items,
            theme=theme,
            on_select=self._navigate,
            on_theme_toggle=self._toggle_theme,
        )
        self.root = ft.Row(
            controls=[self.sidebar.build(), self.content],
            expand=True,
            spacing=0,
        )
        self._navigate(items[0].key)

    # ------------------------------------------------------------------ #
    def build(self) -> ft.Control:
        return ft.Container(
            content=self.root,
            expand=True,
            bgcolor=self.theme.bg,
        )

    # ------------------------------------------------------------------ #
    def _navigate(self, route: str) -> None:
        self.content.content = self.router.render(route)
        self.sidebar.set_active(route)
        self.page.update()

    def _toggle_theme(self) -> None:
        self.theme.toggle()
        self.theme.apply(self.page)
        self.on_theme_toggle()
        # Rebuild sidebar to re-apply colours
        self.sidebar.refresh()
        self.page.update()
