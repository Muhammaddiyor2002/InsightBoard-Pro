"""Reports page — export center + history."""

from __future__ import annotations

import flet as ft

from app.analytics import kpi_summary
from app.components.export_center import ExportCenter
from app.components.snackbar import Notifier
from app.pages._common import empty_state, page_header
from app.state import AppState
from app.ui.theme import AppTheme


class ReportsPage:
    def __init__(self, theme: AppTheme, state: AppState, notifier: Notifier) -> None:
        self.theme = theme
        self.state = state
        self.notifier = notifier
        self._history_host = ft.Column(spacing=8)

    def build(self) -> ft.Control:
        if not self.state.has_data():
            return empty_state(self.theme, "No data", "Upload a file first.")
        center = ExportCenter(
            self.theme,
            on_export_csv=self._export_csv,
            on_export_excel=self._export_excel,
            on_export_pdf=self._export_pdf,
            on_export_summary=self._export_summary,
        )
        self._refresh_history()
        return ft.Column(
            controls=[
                page_header(self.theme, "Reports", "Generate exportable artefacts."),
                ft.Container(height=10),
                center.build(),
                ft.Container(height=20),
                ft.Text(
                    "Recent exports",
                    color=self.theme.text,
                    weight=ft.FontWeight.BOLD,
                    size=14,
                ),
                self._history_host,
            ],
            expand=True,
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )

    # ------------------------------------------------------------------ #
    def _export_csv(self) -> None:
        path = self.state.exporter.export_csv(self.state.df)
        self.state.export_log_repo.add("csv", str(path), path.stat().st_size)
        self.notifier.success(f"Saved {path.name}")
        self._refresh_history()

    def _export_excel(self) -> None:
        kpi = {k: str(v) for k, v in kpi_summary(self.state.df).items()}
        extra = {"kpis": _kv_dataframe(kpi)}
        path = self.state.exporter.export_excel(self.state.df, extra_sheets=extra)
        self.state.export_log_repo.add("xlsx", str(path), path.stat().st_size)
        self.notifier.success(f"Saved {path.name}")
        self._refresh_history()

    def _export_pdf(self) -> None:
        kpi = {k: str(v) for k, v in kpi_summary(self.state.df).items()}
        insights = self.state.insights_engine.generate(self.state.df)
        path = self.state.exporter.export_pdf_dashboard(self.state.df, kpis=kpi, insights=insights)
        self.state.export_log_repo.add("pdf", str(path), path.stat().st_size)
        self.notifier.success(f"Saved {path.name}")
        self._refresh_history()

    def _export_summary(self) -> None:
        insights = self.state.insights_engine.generate(self.state.df)
        path = self.state.exporter.export_text_summary(self.state.df, insights=insights)
        self.state.export_log_repo.add("txt", str(path), path.stat().st_size)
        self.notifier.success(f"Saved {path.name}")
        self._refresh_history()

    # ------------------------------------------------------------------ #
    def _refresh_history(self) -> None:
        items = self.state.export_log_repo.list(limit=10)
        rows = [
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.INSERT_DRIVE_FILE, color=self.theme.muted),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    log.path.split("/")[-1],
                                    color=self.theme.text,
                                    weight=ft.FontWeight.W_500,
                                ),
                                ft.Text(
                                    f"{log.kind.upper()}  •  {log.created_at}",
                                    color=self.theme.muted,
                                    size=11,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                    ],
                    spacing=10,
                ),
                bgcolor=self.theme.surface,
                border=ft.border.all(1, self.theme.border),
                border_radius=10,
                padding=12,
            )
            for log in items
        ]
        if not rows:
            rows = [ft.Text("No exports yet.", color=self.theme.muted)]
        self._history_host.controls = rows
        if self._history_host.page:
            self._history_host.update()


def _kv_dataframe(kv: dict[str, str]):
    import pandas as pd

    return pd.DataFrame({"metric": list(kv.keys()), "value": list(kv.values())})
