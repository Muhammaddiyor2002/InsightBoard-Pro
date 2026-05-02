"""Encoding and delimiter sniffing utilities."""

from __future__ import annotations

import csv
from pathlib import Path

import chardet

_COMMON_DELIMS = [",", ";", "\t", "|"]


def detect_encoding(path: Path, sample_bytes: int = 65_536) -> str:
    """Detect the most likely text encoding for *path*.

    Falls back to ``utf-8`` when chardet returns a low-confidence guess.
    """
    p = Path(path)
    with p.open("rb") as fh:
        raw = fh.read(sample_bytes)
    if not raw:
        return "utf-8"
    result = chardet.detect(raw)
    enc = (result.get("encoding") or "utf-8").lower()
    confidence = float(result.get("confidence") or 0.0)
    if confidence < 0.5:
        return "utf-8"
    # Normalise some common edge cases
    if enc in {"ascii"}:
        return "utf-8"
    return enc


def detect_delimiter(path: Path, encoding: str | None = None) -> str:
    """Detect a CSV/TSV delimiter for *path* using csv.Sniffer with a fallback."""
    enc = encoding or detect_encoding(path)
    p = Path(path)
    with p.open("r", encoding=enc, errors="replace") as fh:
        sample = fh.read(8192)
    if not sample:
        return ","
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters="".join(_COMMON_DELIMS))
        return dialect.delimiter
    except csv.Error:
        # Fallback: pick whichever common delimiter appears most often.
        counts = {d: sample.count(d) for d in _COMMON_DELIMS}
        return max(counts, key=lambda d: counts[d]) or ","
