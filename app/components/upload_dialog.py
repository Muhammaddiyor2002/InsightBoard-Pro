"""Upload dialog component — wraps Flet's FilePicker."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.ui.theme import AppTheme


class UploadDialog:
    """Drag-and-drop / browse uploader."""

    def __init__(
        self,
        page: ft.Page,
        theme: AppTheme,
        *,
        on_pick: Callable[[str], None],
        allowed: tuple[str, ...] = ("csv", "tsv", "xlsx", "xls"),
    ) -> None:
        self.page = page
        self.theme = theme
        self.on_pick = on_pick
        self.allowed = allowed
        self._picker = ft.FilePicker(on_result=self._handle_pick)
        if self._picker not in page.overlay:
            page.overlay.append(self._picker)
            page.update()

    def open(self) -> None:
        self._picker.pick_files(
            dialog_title="Select a CSV / Excel file",
            allow_multiple=False,
            allowed_extensions=list(self.allowed),
        )

    def _handle_pick(self, e: ft.FilePickerResultEvent) -> None:
        if e.files:
            self.on_pick(e.files[0].path)

    # ------------------------------------------------------------------ #
    def build_card(self) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.CLOUD_UPLOAD,
                            color=self.theme.primary,
                            size=42,
                        ),
                        alignment=ft.alignment.center,
                    ),
                    ft.Text(
                        "Drop a CSV / Excel file here, or click to browse",
                        color=self.theme.text,
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.Text(
                        "Supports .csv .tsv .xlsx .xls — up to 250 MB",
                        color=self.theme.muted,
                        text_align=ft.TextAlign.CENTER,
                        size=11,
                    ),
                    ft.Container(height=12),
                    ft.FilledButton(
                        text="Browse files",
                        icon=ft.Icons.FOLDER_OPEN,
                        on_click=lambda _: self.open(),
                        style=ft.ButtonStyle(
                            bgcolor=self.theme.primary,
                            color="white",
                        ),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            bgcolor=self.theme.surface,
            border=ft.border.all(2, self.theme.border),
            border_radius=14,
            padding=40,
            on_click=lambda _: self.open(),
            ink=True,
        )
