"""Upload page — file picker + sample loader."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.components.snackbar import Notifier
from app.components.upload_dialog import UploadDialog
from app.pages._common import page_header
from app.state import AppState
from app.ui.theme import AppTheme


class UploadPage:
    def __init__(
        self,
        page: ft.Page,
        theme: AppTheme,
        state: AppState,
        notifier: Notifier,
        *,
        on_loaded: Callable[[], None],
    ) -> None:
        self.page = page
        self.theme = theme
        self.state = state
        self.notifier = notifier
        self.on_loaded = on_loaded
        self.dialog = UploadDialog(page, theme, on_pick=self._handle_pick)

        self._summary = ft.Column(spacing=6)

    def build(self) -> ft.Control:
        sample_path = self.state.config.samples_dir / "sample_sales.csv"
        return ft.Column(
            controls=[
                page_header(
                    self.theme,
                    "Upload data",
                    "Drag and drop a CSV or Excel file, or load the bundled sample.",
                ),
                ft.Container(height=10),
                self.dialog.build_card(),
                ft.Container(height=20),
                ft.Row(
                    controls=[
                        ft.OutlinedButton(
                            "Load bundled sample",
                            icon=ft.Icons.AUTO_GRAPH,
                            on_click=lambda _: self._handle_pick(str(sample_path)),
                        ),
                    ]
                ),
                ft.Container(height=10),
                self._summary,
            ],
            expand=True,
            spacing=8,
        )

    # ------------------------------------------------------------------ #
    def _handle_pick(self, path: str) -> None:
        try:
            loaded, report = self.state.ingest_file(path)
        except (ValueError, OSError) as exc:
            self.notifier.error(f"Upload failed: {exc}")
            return
        self.notifier.success(
            f"Loaded {loaded.source_path.name} — {loaded.rows:,} rows × {loaded.cols} cols"
        )
        self._summary.controls = [
            ft.Text("Last upload", color=self.theme.muted, size=11),
            ft.Text(loaded.source_path.name, color=self.theme.text, weight=ft.FontWeight.W_600),
            ft.Text(
                f"Rows: {loaded.rows:,}  •  Columns: {loaded.cols}  •  "
                f"Duplicates removed: {report.duplicates_removed:,}  •  "
                f"Missing filled: {report.missing_filled:,}",
                color=self.theme.muted,
                size=12,
            ),
        ]
        self.page.update()
        self.on_loaded()
