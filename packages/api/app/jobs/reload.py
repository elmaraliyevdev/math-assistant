"""Detect uvicorn reload mode for simulation job warnings."""

from __future__ import annotations

import os


def is_uvicorn_reload_child() -> bool:
    """Return True when running inside uvicorn's reload worker subprocess."""
    return os.environ.get("RUN_MAIN") == "true"
