"""Typed dataclasses representing rows in the InsightBoard SQLite tables."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class UploadedFile:
    id: int | None
    filename: str
    path: str
    size_bytes: int
    rows: int | None = None
    cols: int | None = None
    delimiter: str | None = None
    encoding: str | None = None
    created_at: str | None = None


@dataclass
class ReportHistory:
    id: int | None
    file_id: int | None
    title: str
    kind: str
    path: str | None = None
    created_at: str | None = None


@dataclass
class SavedFilter:
    id: int | None
    name: str
    payload_json: str
    created_at: str | None = None


@dataclass
class DashboardTemplate:
    id: int | None
    name: str
    layout_json: str
    created_at: str | None = None


@dataclass
class Setting:
    key: str
    value: str


@dataclass
class ExportLog:
    id: int | None
    kind: str
    path: str
    size_bytes: int | None = None
    created_at: str | None = None


def row_to_dict(row: Any) -> dict[str, Any]:
    """Convert a sqlite3.Row to a plain dict."""
    return {k: row[k] for k in row}
