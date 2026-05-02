"""SQLite connection wrapper and schema migrator."""

from __future__ import annotations

import contextlib
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from app.utils.logger import get_logger

log = get_logger("database")


SCHEMA_STATEMENTS: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS uploaded_files (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        filename    TEXT NOT NULL,
        path        TEXT NOT NULL,
        size_bytes  INTEGER NOT NULL,
        rows        INTEGER,
        cols        INTEGER,
        delimiter   TEXT,
        encoding    TEXT,
        created_at  TEXT DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS report_history (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id     INTEGER REFERENCES uploaded_files(id) ON DELETE CASCADE,
        title       TEXT NOT NULL,
        kind        TEXT NOT NULL,
        path        TEXT,
        created_at  TEXT DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS saved_filters (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        name         TEXT NOT NULL UNIQUE,
        payload_json TEXT NOT NULL,
        created_at   TEXT DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS dashboard_templates (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        name         TEXT NOT NULL UNIQUE,
        layout_json  TEXT NOT NULL,
        created_at   TEXT DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS settings (
        key   TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS export_logs (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        kind        TEXT NOT NULL,
        path        TEXT NOT NULL,
        size_bytes  INTEGER,
        created_at  TEXT DEFAULT (datetime('now'))
    );
    """,
)


class Database:
    """Thin wrapper around :mod:`sqlite3` that owns a single connection."""

    def __init__(self, path: Path | str = ":memory:") -> None:
        self.path = Path(path) if path != ":memory:" else path
        if isinstance(self.path, Path):
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False, isolation_level=None)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._conn.execute("PRAGMA journal_mode = WAL;")
        self.migrate()

    # ------------------------------------------------------------------ #
    # Schema                                                              #
    # ------------------------------------------------------------------ #
    def migrate(self) -> None:
        """Apply schema migrations idempotently."""
        cur = self._conn.cursor()
        for stmt in SCHEMA_STATEMENTS:
            cur.execute(stmt)
        self._conn.commit()
        log.debug("database migrations applied (%d statements)", len(SCHEMA_STATEMENTS))

    # ------------------------------------------------------------------ #
    # Connection helpers                                                  #
    # ------------------------------------------------------------------ #
    @property
    def conn(self) -> sqlite3.Connection:
        return self._conn

    @contextmanager
    def cursor(self) -> Iterator[sqlite3.Cursor]:
        cur = self._conn.cursor()
        try:
            yield cur
        finally:
            cur.close()

    def close(self) -> None:
        with contextlib.suppress(sqlite3.Error):  # pragma: no cover
            self._conn.close()
