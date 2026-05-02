"""Smart, pandas-based data cleaning utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import pandas as pd

from app.utils.logger import get_logger

log = get_logger("data_cleaner")

NumericFill = Literal["mean", "median", "zero", "drop", "none"]
CategoryFill = Literal["mode", "unknown", "drop", "none"]


@dataclass
class CleaningReport:
    """Summary of changes made by :class:`DataCleaner`."""

    rows_before: int = 0
    rows_after: int = 0
    duplicates_removed: int = 0
    missing_filled: int = 0
    outliers_flagged: int = 0
    empty_columns_dropped: list[str] = field(default_factory=list)
    columns_converted: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        return {
            "rows_before": self.rows_before,
            "rows_after": self.rows_after,
            "duplicates_removed": self.duplicates_removed,
            "missing_filled": self.missing_filled,
            "outliers_flagged": self.outliers_flagged,
            "empty_columns_dropped": list(self.empty_columns_dropped),
            "columns_converted": dict(self.columns_converted),
        }


@dataclass
class _Options:
    drop_duplicates: bool = True
    drop_empty_cols: bool = True
    numeric_fill: NumericFill = "median"
    category_fill: CategoryFill = "mode"
    parse_dates: bool = True
    flag_outliers: bool = True
    outlier_iqr_mult: float = 1.5


class DataCleaner:
    """One-stop, opinionated cleaning pipeline.

    Each step is also exposed individually so the UI can apply them à-la-carte.
    """

    def __init__(self, **options: object) -> None:
        self.options = _Options(**options)  # type: ignore[arg-type]

    # ---------------------------------------------------------- profiling
    @staticmethod
    def profile(df: pd.DataFrame) -> pd.DataFrame:
        """Return a per-column profile dataframe used by the UI."""
        rows: list[dict[str, object]] = []
        n = len(df) if len(df) else 1
        for col in df.columns:
            s = df[col]
            null_count = int(s.isna().sum())
            rows.append(
                {
                    "column": col,
                    "dtype": str(s.dtype),
                    "non_null": int(s.notna().sum()),
                    "nulls": null_count,
                    "null_pct": round(null_count / n * 100, 2),
                    "unique": int(s.nunique(dropna=True)),
                    "sample": _sample_value(s),
                }
            )
        return pd.DataFrame(rows)

    # ---------------------------------------------------------- pipeline
    def clean(self, df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
        """Run the configured cleaning pipeline and return a report."""
        report = CleaningReport(rows_before=int(len(df)))
        out = df.copy()

        if self.options.drop_empty_cols:
            empty = [c for c in out.columns if out[c].isna().all()]
            out = out.drop(columns=empty)
            report.empty_columns_dropped = empty

        if self.options.drop_duplicates:
            before = len(out)
            out = out.drop_duplicates()
            report.duplicates_removed = before - len(out)

        if self.options.parse_dates:
            for col in out.columns:
                converted = self._maybe_parse_dates(out[col])
                if converted is not None:
                    out[col] = converted
                    report.columns_converted[col] = "datetime64[ns]"

        # Missing values
        before_missing = int(out.isna().sum().sum())
        out = self._fill_missing(out)
        after_missing = int(out.isna().sum().sum())
        report.missing_filled = max(0, before_missing - after_missing)

        if self.options.flag_outliers:
            mask = self._outlier_mask(out)
            report.outliers_flagged = int(mask.sum().sum())
            out["__outlier__"] = mask.any(axis=1)

        report.rows_after = int(len(out))
        return out, report

    # ---------------------------------------------------------- granular ops
    def fill_missing_numeric(self, s: pd.Series) -> pd.Series:
        if self.options.numeric_fill == "mean":
            return s.fillna(s.mean())
        if self.options.numeric_fill == "median":
            return s.fillna(s.median())
        if self.options.numeric_fill == "zero":
            return s.fillna(0)
        if self.options.numeric_fill == "drop":
            return s.dropna()
        return s

    def fill_missing_categorical(self, s: pd.Series) -> pd.Series:
        if self.options.category_fill == "mode":
            mode = s.mode(dropna=True)
            return s.fillna(mode.iloc[0]) if not mode.empty else s
        if self.options.category_fill == "unknown":
            return s.fillna("Unknown")
        if self.options.category_fill == "drop":
            return s.dropna()
        return s

    def _fill_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in df.columns:
            s = df[col]
            if pd.api.types.is_numeric_dtype(s):
                df[col] = self.fill_missing_numeric(s)
            elif pd.api.types.is_datetime64_any_dtype(s):
                continue
            else:
                df[col] = self.fill_missing_categorical(s)
        return df

    @staticmethod
    def _maybe_parse_dates(s: pd.Series) -> pd.Series | None:
        if not pd.api.types.is_object_dtype(s) and not pd.api.types.is_string_dtype(s):
            return None
        sample = s.dropna().astype(str).head(50)
        if sample.empty:
            return None
        try:
            parsed = pd.to_datetime(s, errors="coerce", utc=False)
        except (ValueError, TypeError):
            return None
        if parsed.notna().mean() > 0.8 and parsed.notna().sum() > 1:
            return parsed
        return None

    def _outlier_mask(self, df: pd.DataFrame) -> pd.DataFrame:
        numeric = df.select_dtypes(include=[np.number])
        if numeric.empty:
            return pd.DataFrame(False, index=df.index, columns=[])
        q1 = numeric.quantile(0.25)
        q3 = numeric.quantile(0.75)
        iqr = q3 - q1
        lo = q1 - self.options.outlier_iqr_mult * iqr
        hi = q3 + self.options.outlier_iqr_mult * iqr
        return (numeric < lo) | (numeric > hi)


def _sample_value(s: pd.Series) -> object:
    nn = s.dropna()
    if nn.empty:
        return None
    val = nn.iloc[0]
    return val.item() if hasattr(val, "item") else val
