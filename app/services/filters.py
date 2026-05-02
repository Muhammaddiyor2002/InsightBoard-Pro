"""Composable, JSON-serialisable dataframe filters."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import pandas as pd


@dataclass
class NumericRange:
    column: str
    minimum: float | None = None
    maximum: float | None = None

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.column not in df.columns:
            return df
        series = pd.to_numeric(df[self.column], errors="coerce")
        mask = pd.Series(True, index=df.index)
        if self.minimum is not None:
            mask &= series >= self.minimum
        if self.maximum is not None:
            mask &= series <= self.maximum
        return df[mask]


@dataclass
class Filter:
    """A multi-column filter set; chains in declaration order."""

    text_search: str = ""
    text_columns: list[str] = field(default_factory=list)
    categorical: dict[str, list[Any]] = field(default_factory=dict)
    numeric_ranges: list[NumericRange] = field(default_factory=list)
    date_column: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "text_search": self.text_search,
            "text_columns": list(self.text_columns),
            "categorical": {k: list(v) for k, v in self.categorical.items()},
            "numeric_ranges": [vars(r) for r in self.numeric_ranges],
            "date_column": self.date_column,
            "date_from": self.date_from.isoformat() if self.date_from else None,
            "date_to": self.date_to.isoformat() if self.date_to else None,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Filter:
        nr = [NumericRange(**d) for d in payload.get("numeric_ranges", [])]
        return cls(
            text_search=payload.get("text_search", ""),
            text_columns=list(payload.get("text_columns", [])),
            categorical={k: list(v) for k, v in payload.get("categorical", {}).items()},
            numeric_ranges=nr,
            date_column=payload.get("date_column"),
            date_from=_iso_to_dt(payload.get("date_from")),
            date_to=_iso_to_dt(payload.get("date_to")),
        )


def _iso_to_dt(v: Any) -> datetime | None:
    if not v:
        return None
    return datetime.fromisoformat(v) if isinstance(v, str) else v


class FilterEngine:
    """Apply :class:`Filter` instances against a dataframe."""

    def apply(self, df: pd.DataFrame, flt: Filter) -> pd.DataFrame:
        out = df

        # categorical filters
        for col, values in flt.categorical.items():
            if not values or col not in out.columns:
                continue
            out = out[out[col].isin(values)]

        # numeric ranges
        for nr in flt.numeric_ranges:
            out = nr.apply(out)

        # date range
        if flt.date_column and flt.date_column in out.columns:
            series = pd.to_datetime(out[flt.date_column], errors="coerce")
            mask = pd.Series(True, index=out.index)
            if flt.date_from is not None:
                mask &= series >= pd.Timestamp(flt.date_from)
            if flt.date_to is not None:
                mask &= series <= pd.Timestamp(flt.date_to)
            out = out[mask]

        # text search across selected columns (or all object columns when empty)
        if flt.text_search:
            cols = flt.text_columns or [
                c for c in out.columns if pd.api.types.is_object_dtype(out[c])
            ]
            if cols:
                pat = flt.text_search
                masks = [
                    out[c].astype(str).str.contains(pat, case=False, na=False)
                    for c in cols
                    if c in out.columns
                ]
                if masks:
                    combined = masks[0]
                    for m in masks[1:]:
                        combined = combined | m
                    out = out[combined]

        return out
