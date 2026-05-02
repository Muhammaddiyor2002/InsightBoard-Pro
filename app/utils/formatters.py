"""Human-friendly value formatters used throughout the UI."""

from __future__ import annotations

import math
from typing import Any

_SUFFIXES = ["", "K", "M", "B", "T"]


def human_number(value: Any, decimals: int = 1) -> str:
    """Format a number with K/M/B/T suffixes.

    >>> human_number(1234)
    '1.2K'
    >>> human_number(0)
    '0'
    """
    try:
        n = float(value)
    except (TypeError, ValueError):
        return str(value)
    if n != n or math.isinf(n):  # NaN / inf
        return "—"
    if n == 0:
        return "0"
    sign = "-" if n < 0 else ""
    n = abs(n)
    idx = min(len(_SUFFIXES) - 1, int(math.log10(n) // 3)) if n >= 1 else 0
    scaled = n / (10 ** (3 * idx))
    if idx == 0:
        if scaled == int(scaled):
            return f"{sign}{int(scaled)}"
        return f"{sign}{scaled:.{decimals}f}"
    return f"{sign}{scaled:.{decimals}f}{_SUFFIXES[idx]}"


def human_bytes(size: float) -> str:
    """Format a byte count in IEC units."""
    if size <= 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    idx = min(len(units) - 1, int(math.log(size, 1024)))
    return f"{size / (1024**idx):.1f} {units[idx]}"


def percent(numer: float, denom: float, decimals: int = 1) -> str:
    """Format a percentage with safe division."""
    if denom == 0:
        return "0%"
    return f"{(numer / denom) * 100:.{decimals}f}%"
