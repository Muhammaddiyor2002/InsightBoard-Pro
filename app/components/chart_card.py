"""Chart card — wraps a Plotly figure in a styled Flet container."""

from __future__ import annotations

import base64
from collections.abc import Callable

import flet as ft
import plotly.graph_objects as go

from app.ui.theme import AppTheme
from app.utils.logger import get_logger

log = get_logger("chart_card")


class ChartCard:
    """Render a Plotly figure inside a card with a title and toolbar."""

    def __init__(
        self,
        theme: AppTheme,
        *,
        title: str,
        figure: go.Figure,
        height: int = 380,
        on_export: Callable[[go.Figure], None] | None = None,
    ) -> None:
        self.theme = theme
        self.title = title
        self.figure = figure
        self.height = height
        self.on_export = on_export

    def build(self) -> ft.Control:
        chart_control = self._render_plotly(self.figure)
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                self.title,
                                color=self.theme.text,
                                weight=ft.FontWeight.W_600,
                                size=14,
                            ),
                            ft.Container(expand=True),
                            ft.IconButton(
                                ft.Icons.DOWNLOAD,
                                icon_color=self.theme.muted,
                                tooltip="Export PNG",
                                on_click=lambda _: (
                                    self.on_export(self.figure) if self.on_export else None
                                ),
                            ),
                        ],
                    ),
                    ft.Container(
                        content=chart_control,
                        height=self.height,
                        expand=True,
                    ),
                ],
                spacing=8,
            ),
            bgcolor=self.theme.surface,
            border=ft.border.all(1, self.theme.border),
            border_radius=14,
            padding=16,
        )

    # ------------------------------------------------------------------ #
    def _render_plotly(self, figure: go.Figure) -> ft.Control:
        """Try Flet's PlotlyChart; otherwise fall back to a static PNG image."""
        try:
            import flet.plotly_chart as fpc

            return fpc.PlotlyChart(figure, expand=True)
        except (ImportError, AttributeError):
            pass
        try:
            from flet_contrib.plotly_chart import PlotlyChart

            return PlotlyChart(figure, expand=True)
        except (ImportError, AttributeError):
            pass
        # Static fallback via kaleido
        try:
            png = figure.to_image(format="png", width=900, height=self.height, engine="kaleido")
            return ft.Image(
                src_base64=base64.b64encode(png).decode("ascii"),
                fit=ft.ImageFit.CONTAIN,
                expand=True,
            )
        except (ValueError, RuntimeError) as exc:  # pragma: no cover
            log.warning("plotly render fallback failed: %s", exc)
            return ft.Text("Chart unavailable", color=self.theme.muted)
