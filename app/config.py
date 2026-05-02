"""Centralised application configuration.

The :class:`AppConfig` dataclass is the single source of truth for runtime
paths, limits, theme defaults and feature toggles. Tests and modules that
need configuration values should depend on an :class:`AppConfig` instance
rather than hard-coding values; this keeps the codebase trivially testable
and lets us override settings (e.g. `tmp_path` directories) at runtime.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _project_root() -> Path:
    """Resolve the project root directory regardless of cwd."""
    return Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class AppConfig:
    """Runtime configuration for InsightBoard Pro."""

    app_name: str = "InsightBoard Pro"
    version: str = "1.0.0"

    # Paths
    project_root: Path = field(default_factory=_project_root)
    data_dir: Path = field(default_factory=lambda: _project_root() / "data")
    samples_dir: Path = field(default_factory=lambda: _project_root() / "data" / "samples")
    exports_dir: Path = field(default_factory=lambda: _project_root() / "exports")
    db_path: Path = field(default_factory=lambda: _project_root() / "data" / "insightboard.sqlite")

    # Limits / safety
    max_file_size_mb: int = 250
    max_preview_rows: int = 200
    max_table_rows_in_ui: int = 5_000
    allowed_extensions: tuple[str, ...] = (".csv", ".tsv", ".xlsx", ".xls")

    # UI defaults
    default_theme: str = "dark"
    sidebar_width: int = 240
    sidebar_collapsed_width: int = 72

    # Performance
    use_duckdb: bool = True
    chart_max_points: int = 50_000

    @classmethod
    def from_env(cls) -> AppConfig:
        """Build a config, applying overrides from environment variables."""
        kwargs: dict[str, object] = {}
        if v := os.environ.get("INSIGHTBOARD_MAX_FILE_MB"):
            kwargs["max_file_size_mb"] = int(v)
        if v := os.environ.get("INSIGHTBOARD_THEME"):
            kwargs["default_theme"] = v
        if v := os.environ.get("INSIGHTBOARD_DB"):
            kwargs["db_path"] = Path(v)
        return cls(**kwargs)  # type: ignore[arg-type]

    def ensure_dirs(self) -> None:
        """Create runtime directories if missing."""
        for path in (self.data_dir, self.samples_dir, self.exports_dir):
            path.mkdir(parents=True, exist_ok=True)
