"""Structured logging helpers."""

from __future__ import annotations

import logging
import sys
from logging import Logger

_CONFIGURED = False


def _configure_root() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    root = logging.getLogger("insightboard")
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    root.propagate = False
    _CONFIGURED = True


def get_logger(name: str) -> Logger:
    """Return a namespaced logger; root handler is configured lazily."""
    _configure_root()
    return logging.getLogger(f"insightboard.{name}")
