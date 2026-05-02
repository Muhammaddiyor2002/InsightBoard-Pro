"""Dashboard page — KPI cards + Auto Insights."""

from __future__ import annotations

from datetime import datetime

import flet as ft

from app.analytics import kpi_summary
from app.components.kpi_card import KpiCard
from app.pages._common import empty_state, page_header
from app.state import AppState
from app.ui.theme import AppTheme
from app.utils.formatters import human_number


class DashboardPage:
    def __init__(self, theme: AppTheme, state: AppState) -> None:
        self.theme = theme
        self.state = state

    def build(self) -> ft.Control:
        if not self.state.has_data():
            return empty_state(
                self.theme,
                "Dashboard waiting for data",
                "Upload a CSV / Excel file to see KPIs and auto-insights.",
            )
        df = self.state.df
        kpi = kpi_summary(df)
        cards = [
            KpiCard(
                self.theme,
                title="Total rows",
                value=human_number(kpi["rows"]),
                sub=f"{kpi['rows']:,} records",
                icon=ft.Icons.NUMBERS,
            ).build(),
            KpiCard(
                self.theme,
                title="Total columns",
                value=str(kpi["columns"]),
                sub=f"{kpi['numeric_columns']} numeric · {kpi['categorical_columns']} cat · {kpi['date_columns']} date",
                icon=ft.Icons.VIEW_COLUMN,
                accent=self.theme.accent,
            ).build(),
            KpiCard(
                self.theme,
                title="Missing values",
                value=human_number(kpi["missing_values"]),
                sub="Imputed by smart cleaner",
                icon=ft.Icons.WARNING_AMBER,
                accent=self.theme.warning,
            ).build(),
            KpiCard(
                self.theme,
                title="Duplicate rows",
                value=human_number(kpi["duplicate_rows"]),
                sub="Removed during ingest",
                icon=ft.Icons.CONTENT_COPY,
                accent=self.theme.danger,
            ).build(),
            KpiCard(
                self.theme,
                title="Numeric cols",
                value=str(kpi["numeric_columns"]),
                sub="Quantitative metrics",
                icon=ft.Icons.STACKED_LINE_CHART,
            ).build(),
            KpiCard(
                self.theme,
                title="Category cols",
                value=str(kpi["categorical_columns"]),
                sub="Qualitative dimensions",
                icon=ft.Icons.LABEL,
                accent=self.theme.accent,
            ).build(),
            KpiCard(
                self.theme,
                title="Date cols",
                value=str(kpi["date_columns"]),
                sub="Time dimensions",
                icon=ft.Icons.CALENDAR_MONTH,
                accent=self.theme.success,
            ).build(),
            KpiCard(
                self.theme,
                title="Last updated",
                value=datetime.now().strftime("%H:%M"),
                sub=datetime.now().strftime("%Y-%m-%d"),
                icon=ft.Icons.SCHEDULE,
                accent=self.theme.muted,
            ).build(),
        ]
        kpi_grid = ft.GridView(
            controls=cards,
            runs_count=4,
            max_extent=300,
            child_aspect_ratio=1.7,
            spacing=12,
            run_spacing=12,
        )

        insights = self.state.insights_engine.generate(df)
        insight_cards = [self._insight_card(i) for i in insights]
        if not insight_cards:
            insight_cards = [ft.Text("No specific insights at the moment.", color=self.theme.muted)]

        return ft.Column(
            controls=[
                page_header(self.theme, "Dashboard", "Live KPIs and auto-generated insights."),
                ft.Container(height=10),
                kpi_grid,
                ft.Container(height=20),
                ft.Text(
                    "Auto-insights",
                    color=self.theme.text,
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Column(controls=insight_cards, spacing=10),
            ],
            expand=True,
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )

    # ------------------------------------------------------------------ #
    def _insight_card(self, insight) -> ft.Control:
        accent_map = {
            "trend": self.theme.success,
            "spike": self.theme.warning,
            "anomaly": self.theme.danger,
            "top": self.theme.primary,
            "stat": self.theme.accent,
        }
        accent = accent_map.get(insight.kind, self.theme.primary)
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(ft.Icons.AUTO_AWESOME, color="white", size=18),
                        bgcolor=accent,
                        padding=10,
                        border_radius=10,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                insight.title, color=self.theme.text, weight=ft.FontWeight.W_600
                            ),
                            ft.Text(insight.detail, color=self.theme.muted, size=12),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Text(
                            insight.kind.upper(),
                            color="white",
                            size=10,
                            weight=ft.FontWeight.BOLD,
                        ),
                        bgcolor=accent,
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        border_radius=20,
                    ),
                ],
                spacing=12,
            ),
            bgcolor=self.theme.surface,
            border=ft.border.all(1, self.theme.border),
            border_radius=12,
            padding=14,
        )
