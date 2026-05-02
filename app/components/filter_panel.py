"""Multi-column filter panel."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

import flet as ft
import numpy as np
import pandas as pd

from app.services.filters import Filter, NumericRange
from app.ui.theme import AppTheme


class FilterPanel:
    """A composable filter panel that fires a callback whenever filters change."""

    def __init__(
        self,
        theme: AppTheme,
        *,
        df: pd.DataFrame,
        on_change: Callable[[Filter], None],
    ) -> None:
        self.theme = theme
        self.df = df
        self.on_change = on_change
        self.current = Filter()

        self._search = ft.TextField(
            label="Search",
            hint_text="text contains…",
            on_change=self._handle_search,
            border_color=self.theme.border,
            color=self.theme.text,
        )
        self._categorical_controls: dict[str, ft.Dropdown] = {}
        self._numeric_controls: dict[str, tuple[ft.TextField, ft.TextField]] = {}
        self._date_controls: dict[str, ft.TextField] = {}

    def build(self) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Filters",
                        color=self.theme.text,
                        weight=ft.FontWeight.BOLD,
                        size=16,
                    ),
                    self._search,
                    ft.Divider(color=self.theme.border, height=1),
                    ft.Text("Categorical", color=self.theme.muted, size=11),
                    *self._categorical_dropdowns(),
                    ft.Divider(color=self.theme.border, height=1),
                    ft.Text("Numeric", color=self.theme.muted, size=11),
                    *self._numeric_inputs(),
                    ft.Divider(color=self.theme.border, height=1),
                    ft.Text("Date range", color=self.theme.muted, size=11),
                    *self._date_inputs(),
                    ft.Container(height=8),
                    ft.Row(
                        controls=[
                            ft.OutlinedButton(
                                "Reset",
                                icon=ft.Icons.REFRESH,
                                on_click=lambda _: self._reset(),
                            ),
                        ]
                    ),
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            ),
            bgcolor=self.theme.surface,
            border=ft.border.all(1, self.theme.border),
            border_radius=14,
            padding=16,
            width=300,
        )

    # ------------------------------------------------------------------ #
    def _categorical_dropdowns(self) -> list[ft.Control]:
        controls: list[ft.Control] = []
        cats = [
            c
            for c in self.df.columns
            if not pd.api.types.is_numeric_dtype(self.df[c])
            and not pd.api.types.is_datetime64_any_dtype(self.df[c])
            and 1 < self.df[c].nunique() <= 50
        ]
        for col in cats[:5]:
            options = [ft.dropdown.Option("(all)")]
            options += [
                ft.dropdown.Option(str(v))
                for v in sorted(self.df[col].dropna().unique().tolist(), key=str)[:50]
            ]
            dd = ft.Dropdown(
                label=col,
                options=options,
                value="(all)",
                on_change=lambda e, c=col: self._handle_category(c, e.control.value),
                border_color=self.theme.border,
                color=self.theme.text,
            )
            self._categorical_controls[col] = dd
            controls.append(dd)
        if not controls:
            controls.append(ft.Text("No categorical columns", color=self.theme.muted, size=11))
        return controls

    def _numeric_inputs(self) -> list[ft.Control]:
        controls: list[ft.Control] = []
        nums = self.df.select_dtypes(include=[np.number]).columns.tolist()
        for col in nums[:4]:
            mn = ft.TextField(
                label=f"{col} min",
                width=130,
                color=self.theme.text,
                border_color=self.theme.border,
                on_change=lambda _e, c=col: self._handle_numeric(c),
            )
            mx = ft.TextField(
                label=f"{col} max",
                width=130,
                color=self.theme.text,
                border_color=self.theme.border,
                on_change=lambda _e, c=col: self._handle_numeric(c),
            )
            self._numeric_controls[col] = (mn, mx)
            controls.append(ft.Row(controls=[mn, mx], spacing=8))
        if not controls:
            controls.append(ft.Text("No numeric columns", color=self.theme.muted, size=11))
        return controls

    def _date_inputs(self) -> list[ft.Control]:
        controls: list[ft.Control] = []
        dates = self.df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
        if not dates:
            controls.append(ft.Text("No date columns", color=self.theme.muted, size=11))
            return controls
        col = dates[0]
        self.current.date_column = col
        d_from = ft.TextField(
            label=f"{col} from (YYYY-MM-DD)",
            color=self.theme.text,
            border_color=self.theme.border,
            on_change=lambda _: self._handle_dates(),
        )
        d_to = ft.TextField(
            label=f"{col} to (YYYY-MM-DD)",
            color=self.theme.text,
            border_color=self.theme.border,
            on_change=lambda _: self._handle_dates(),
        )
        self._date_controls = {"from": d_from, "to": d_to}
        controls.extend([d_from, d_to])
        return controls

    # ------------------------------------------------------------------ #
    def _handle_search(self, _: ft.ControlEvent) -> None:
        self.current.text_search = self._search.value or ""
        self.on_change(self.current)

    def _handle_category(self, column: str, value: str | None) -> None:
        if not value or value == "(all)":
            self.current.categorical.pop(column, None)
        else:
            self.current.categorical[column] = [_coerce(value, self.df[column])]
        self.on_change(self.current)

    def _handle_numeric(self, column: str) -> None:
        mn, mx = self._numeric_controls[column]
        try:
            mn_val = float(mn.value) if mn.value else None
        except ValueError:
            mn_val = None
        try:
            mx_val = float(mx.value) if mx.value else None
        except ValueError:
            mx_val = None
        ranges = [r for r in self.current.numeric_ranges if r.column != column]
        if mn_val is not None or mx_val is not None:
            ranges.append(NumericRange(column=column, minimum=mn_val, maximum=mx_val))
        self.current.numeric_ranges = ranges
        self.on_change(self.current)

    def _handle_dates(self) -> None:
        d_from = self._date_controls.get("from")
        d_to = self._date_controls.get("to")
        self.current.date_from = _parse_date(d_from.value) if d_from else None
        self.current.date_to = _parse_date(d_to.value) if d_to else None
        self.on_change(self.current)

    def _reset(self) -> None:
        self.current = Filter()
        self._search.value = ""
        for dd in self._categorical_controls.values():
            dd.value = "(all)"
        for mn, mx in self._numeric_controls.values():
            mn.value = ""
            mx.value = ""
        for tf in self._date_controls.values():
            tf.value = ""
        self.on_change(self.current)


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _coerce(value: str, series: pd.Series) -> object:
    if pd.api.types.is_numeric_dtype(series):
        try:
            return float(value)
        except ValueError:
            return value
    return value
