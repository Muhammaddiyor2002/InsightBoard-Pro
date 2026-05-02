"""Data Preview page — column profile + data table."""

from __future__ import annotations

import flet as ft

from app.components.data_table import DataTableViewer
from app.pages._common import empty_state, page_header
from app.services import DataCleaner
from app.state import AppState
from app.ui.theme import AppTheme


class PreviewPage:
    def __init__(self, theme: AppTheme, state: AppState) -> None:
        self.theme = theme
        self.state = state

    def build(self) -> ft.Control:
        if not self.state.has_data():
            return empty_state(
                self.theme,
                "No dataset loaded",
                "Open the Upload page and pick a file to start exploring.",
            )
        df = self.state.cleaned
        assert df is not None
        profile = DataCleaner.profile(df)
        viewer = DataTableViewer(self.theme, df=df.head(self.state.config.max_table_rows_in_ui))
        profile_viewer = DataTableViewer(self.theme, df=profile, page_size=15)

        tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(
                    text="Sample rows",
                    content=ft.Container(
                        content=viewer.build(),
                        padding=ft.padding.only(top=10),
                    ),
                ),
                ft.Tab(
                    text="Column profile",
                    content=ft.Container(
                        content=profile_viewer.build(),
                        padding=ft.padding.only(top=10),
                    ),
                ),
            ],
            label_color=self.theme.text,
            unselected_label_color=self.theme.muted,
            indicator_color=self.theme.primary,
            divider_color=self.theme.border,
            expand=True,
        )

        return ft.Column(
            controls=[
                page_header(
                    self.theme,
                    "Data preview",
                    f"{len(df):,} rows · {df.shape[1]} columns",
                ),
                ft.Container(height=10),
                tabs,
            ],
            expand=True,
            spacing=10,
        )
