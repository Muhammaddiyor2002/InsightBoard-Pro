"""Universal CSV / Excel loader with autodetection."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from app.utils.encoding import detect_delimiter, detect_encoding
from app.utils.logger import get_logger
from app.utils.validators import validate_file

log = get_logger("file_loader")


@dataclass
class LoadedDataset:
    """Result of loading a tabular file."""

    df: pd.DataFrame
    source_path: Path
    delimiter: str | None = None
    encoding: str | None = None
    sheet_name: str | None = None
    detected_dtypes: dict[str, str] = field(default_factory=dict)

    @property
    def rows(self) -> int:
        return int(len(self.df))

    @property
    def cols(self) -> int:
        return int(self.df.shape[1])

    @property
    def size_bytes(self) -> int:
        try:
            return self.source_path.stat().st_size
        except OSError:
            return 0


class FileLoader:
    """Loads CSV / TSV / XLSX / XLS files into pandas DataFrames."""

    def __init__(
        self,
        *,
        max_size_mb: int = 250,
        allowed_extensions: tuple[str, ...] = (".csv", ".tsv", ".xlsx", ".xls"),
    ) -> None:
        self.max_size_mb = max_size_mb
        self.allowed_extensions = allowed_extensions

    # ------------------------------------------------------------------ #
    # Public API                                                          #
    # ------------------------------------------------------------------ #
    def load(self, path: str | Path, *, sheet_name: str | int | None = 0) -> LoadedDataset:
        p = Path(path)
        result = validate_file(
            p,
            allowed_extensions=self.allowed_extensions,
            max_size_mb=self.max_size_mb,
        )
        if not result.ok:
            raise ValueError(result.message)

        ext = p.suffix.lower()
        if ext in {".csv", ".tsv"}:
            return self._load_csv(p)
        if ext in {".xlsx", ".xls"}:
            return self._load_excel(p, sheet_name=sheet_name)
        raise ValueError(f"Unsupported extension: {ext}")  # pragma: no cover

    def list_excel_sheets(self, path: str | Path) -> list[str]:
        p = Path(path)
        return list(pd.ExcelFile(p).sheet_names)

    # ------------------------------------------------------------------ #
    # Private helpers                                                     #
    # ------------------------------------------------------------------ #
    def _load_csv(self, path: Path) -> LoadedDataset:
        encoding = detect_encoding(path)
        delim = detect_delimiter(path, encoding=encoding)
        log.info("loading csv %s enc=%s delim=%r", path.name, encoding, delim)
        df = pd.read_csv(
            path,
            sep=delim,
            encoding=encoding,
            engine="python",
            on_bad_lines="skip",
        )
        df = self._post_process(df)
        return LoadedDataset(
            df=df,
            source_path=path,
            delimiter=delim,
            encoding=encoding,
            detected_dtypes=_dtype_map(df),
        )

    def _load_excel(self, path: Path, *, sheet_name: Any) -> LoadedDataset:
        log.info("loading excel %s sheet=%s", path.name, sheet_name)
        df = pd.read_excel(path, sheet_name=sheet_name)
        if isinstance(df, dict):
            # Multiple sheets — pick the first
            sheet_name, df = next(iter(df.items()))
        df = self._post_process(df)
        return LoadedDataset(
            df=df,
            source_path=path,
            sheet_name=str(sheet_name) if sheet_name is not None else None,
            detected_dtypes=_dtype_map(df),
        )

    @staticmethod
    def _post_process(df: pd.DataFrame) -> pd.DataFrame:
        # Strip whitespace from string columns and column names
        df = df.rename(columns=lambda c: str(c).strip())
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype("string").str.strip()
        # Best-effort datetime parse for text columns whose string
        # representation matches common date formats.
        for col in df.select_dtypes(include=["object", "string"]).columns:
            sample = df[col].dropna().astype(str).head(20)
            if sample.empty:
                continue
            if (
                sample.str.match(r"^\d{4}-\d{2}-\d{2}").mean() > 0.8
                or sample.str.match(r"^\d{1,2}/\d{1,2}/\d{2,4}").mean() > 0.8
            ):
                parsed = pd.to_datetime(df[col], errors="coerce", utc=False)
                if parsed.notna().mean() > 0.8:
                    df[col] = parsed
        return df


def _dtype_map(df: pd.DataFrame) -> dict[str, str]:
    return {col: str(dtype) for col, dtype in df.dtypes.items()}
