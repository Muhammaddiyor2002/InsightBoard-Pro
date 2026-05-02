"""InsightBoard Pro — Flet application entry point."""

from __future__ import annotations

import flet as ft

from app import __version__
from app.components.sidebar import SidebarItem
from app.components.snackbar import Notifier
from app.config import AppConfig
from app.database import Database
from app.pages import (
    ChartsPage,
    DashboardPage,
    FiltersPage,
    HistoryPage,
    HomePage,
    PreviewPage,
    ReportsPage,
    SettingsPage,
    UploadPage,
)
from app.state import AppState
from app.ui.layout import AppLayout
from app.ui.router import Router
from app.ui.theme import AppTheme
from app.utils.logger import get_logger

log = get_logger("main")


SIDEBAR = [
    SidebarItem("home", "Home", ft.Icons.HOME),
    SidebarItem("upload", "Upload Data", ft.Icons.CLOUD_UPLOAD),
    SidebarItem("preview", "Data Preview", ft.Icons.TABLE_VIEW),
    SidebarItem("dashboard", "Dashboard", ft.Icons.DASHBOARD),
    SidebarItem("charts", "Charts", ft.Icons.SHOW_CHART),
    SidebarItem("filters", "Filters", ft.Icons.FILTER_ALT),
    SidebarItem("reports", "Reports", ft.Icons.PICTURE_AS_PDF),
    SidebarItem("history", "History", ft.Icons.HISTORY),
    SidebarItem("settings", "Settings", ft.Icons.SETTINGS),
]


def main(page: ft.Page) -> None:
    """Flet entry point — bootstraps state, theme and router."""
    config = AppConfig.from_env()
    config.ensure_dirs()
    log.info("starting %s v%s", config.app_name, __version__)

    page.title = config.app_name
    page.window.width = 1440
    page.window.height = 900
    page.window.min_width = 1100
    page.window.min_height = 720
    page.padding = 0
    page.spacing = 0

    theme = AppTheme(mode=config.default_theme)
    theme.apply(page)

    db = Database(config.db_path)
    state = AppState(config=config, db=db)
    notifier = Notifier(page, theme)

    router = Router()
    layout: AppLayout | None = None  # noqa: PLR1714 - filled below

    def navigate(route: str) -> None:
        if layout is not None:
            layout._navigate(route)  # noqa: SLF001 - intentional internal call

    router.register(
        "home",
        lambda: HomePage(theme, on_navigate=navigate, version=__version__).build(),
        default=True,
    )
    router.register(
        "upload",
        lambda: UploadPage(
            page,
            theme,
            state,
            notifier,
            on_loaded=lambda: navigate("dashboard"),
        ).build(),
    )
    router.register("preview", lambda: PreviewPage(theme, state).build())
    router.register("dashboard", lambda: DashboardPage(theme, state).build())
    router.register("charts", lambda: ChartsPage(theme, state, notifier).build())
    router.register("filters", lambda: FiltersPage(theme, state).build())
    router.register("reports", lambda: ReportsPage(theme, state, notifier).build())
    router.register("history", lambda: HistoryPage(theme, state).build())
    router.register(
        "settings",
        lambda: SettingsPage(
            theme,
            config,
            on_theme_toggle=lambda: layout._toggle_theme() if layout else None,  # noqa: SLF001
        ).build(),
    )

    layout = AppLayout(
        page=page,
        theme=theme,
        router=router,
        items=SIDEBAR,
        on_theme_toggle=lambda: None,
    )
    page.add(layout.build())

    state.subscribe(lambda: navigate("dashboard"))


def run() -> None:
    """Console-script entry point."""
    ft.app(target=main)


if __name__ == "__main__":  # pragma: no cover
    run()
