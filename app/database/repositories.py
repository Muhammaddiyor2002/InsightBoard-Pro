"""Repository classes that hide raw SQL behind type-safe APIs."""

from __future__ import annotations

import json
from typing import Any

from app.database.db import Database
from app.database.models import (
    DashboardTemplate,
    ExportLog,
    ReportHistory,
    SavedFilter,
    Setting,
    UploadedFile,
)


class _BaseRepo:
    def __init__(self, db: Database) -> None:
        self.db = db


class UploadedFileRepo(_BaseRepo):
    def add(self, file: UploadedFile) -> int:
        with self.db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO uploaded_files
                    (filename, path, size_bytes, rows, cols, delimiter, encoding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    file.filename,
                    file.path,
                    file.size_bytes,
                    file.rows,
                    file.cols,
                    file.delimiter,
                    file.encoding,
                ),
            )
            return int(cur.lastrowid or 0)

    def list(self, limit: int = 50) -> list[UploadedFile]:
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT * FROM uploaded_files ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            return [UploadedFile(**dict(r)) for r in cur.fetchall()]

    def get(self, file_id: int) -> UploadedFile | None:
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM uploaded_files WHERE id = ?", (file_id,))
            row = cur.fetchone()
            return UploadedFile(**dict(row)) if row else None

    def delete(self, file_id: int) -> None:
        with self.db.cursor() as cur:
            cur.execute("DELETE FROM uploaded_files WHERE id = ?", (file_id,))


class ReportHistoryRepo(_BaseRepo):
    def add(self, report: ReportHistory) -> int:
        with self.db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO report_history (file_id, title, kind, path)
                VALUES (?, ?, ?, ?)
                """,
                (report.file_id, report.title, report.kind, report.path),
            )
            return int(cur.lastrowid or 0)

    def list(self, limit: int = 50) -> list[ReportHistory]:
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT * FROM report_history ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            return [ReportHistory(**dict(r)) for r in cur.fetchall()]


class SavedFilterRepo(_BaseRepo):
    def upsert(self, name: str, payload: dict[str, Any]) -> int:
        body = json.dumps(payload, default=str)
        with self.db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO saved_filters (name, payload_json) VALUES (?, ?)
                ON CONFLICT(name) DO UPDATE SET payload_json = excluded.payload_json
                """,
                (name, body),
            )
            cur.execute("SELECT id FROM saved_filters WHERE name = ?", (name,))
            row = cur.fetchone()
            return int(row["id"]) if row else 0

    def list(self) -> list[SavedFilter]:
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM saved_filters ORDER BY id DESC")
            return [SavedFilter(**dict(r)) for r in cur.fetchall()]

    def get(self, name: str) -> dict[str, Any] | None:
        with self.db.cursor() as cur:
            cur.execute("SELECT payload_json FROM saved_filters WHERE name = ?", (name,))
            row = cur.fetchone()
            return json.loads(row["payload_json"]) if row else None


class DashboardTemplateRepo(_BaseRepo):
    def upsert(self, name: str, layout: dict[str, Any]) -> int:
        body = json.dumps(layout, default=str)
        with self.db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO dashboard_templates (name, layout_json) VALUES (?, ?)
                ON CONFLICT(name) DO UPDATE SET layout_json = excluded.layout_json
                """,
                (name, body),
            )
            cur.execute("SELECT id FROM dashboard_templates WHERE name = ?", (name,))
            row = cur.fetchone()
            return int(row["id"]) if row else 0

    def list(self) -> list[DashboardTemplate]:
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM dashboard_templates ORDER BY id DESC")
            return [DashboardTemplate(**dict(r)) for r in cur.fetchall()]


class SettingsRepo(_BaseRepo):
    def set(self, key: str, value: str) -> None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )

    def get(self, key: str, default: str | None = None) -> str | None:
        with self.db.cursor() as cur:
            cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cur.fetchone()
            return row["value"] if row else default

    def all(self) -> list[Setting]:
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM settings ORDER BY key")
            return [Setting(**dict(r)) for r in cur.fetchall()]


class ExportLogRepo(_BaseRepo):
    def add(self, kind: str, path: str, size_bytes: int | None = None) -> int:
        with self.db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO export_logs (kind, path, size_bytes)
                VALUES (?, ?, ?)
                """,
                (kind, path, size_bytes),
            )
            return int(cur.lastrowid or 0)

    def list(self, limit: int = 50) -> list[ExportLog]:
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT * FROM export_logs ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            return [ExportLog(**dict(r)) for r in cur.fetchall()]
