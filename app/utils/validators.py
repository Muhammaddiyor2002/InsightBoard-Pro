"""File / input validators used by the upload pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationResult:
    ok: bool
    message: str = ""


def validate_file(
    path: Path | str,
    *,
    allowed_extensions: tuple[str, ...] = (".csv", ".tsv", ".xlsx", ".xls"),
    max_size_mb: int = 250,
) -> ValidationResult:
    """Validate that *path* is a readable file with an allowed extension and size."""
    p = Path(path)
    if not p.exists():
        return ValidationResult(False, f"File not found: {p}")
    if not p.is_file():
        return ValidationResult(False, f"Not a regular file: {p}")
    ext = p.suffix.lower()
    if ext not in allowed_extensions:
        return ValidationResult(
            False,
            f"Unsupported extension '{ext}'. Allowed: {', '.join(allowed_extensions)}",
        )
    size_mb = p.stat().st_size / (1024 * 1024)
    if size_mb > max_size_mb:
        return ValidationResult(
            False,
            f"File is {size_mb:.1f} MB which exceeds the {max_size_mb} MB limit.",
        )
    if size_mb == 0:
        return ValidationResult(False, "File is empty.")
    return ValidationResult(True, "ok")


def sanitize_column_name(name: str) -> str:
    """Sanitise a column name for safe display / SQL usage."""
    safe = "".join(ch if ch.isalnum() or ch in {"_", " "} else "_" for ch in name).strip()
    return safe or "column"
