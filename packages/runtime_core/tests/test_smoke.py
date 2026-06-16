"""Smoke tests verifying Phase M0 tooling and package wiring."""

from runtime_core import ENGINE_VERSION
from runtime_core.common.logging import get_logger


def test_engine_version_is_pinned() -> None:
    assert ENGINE_VERSION.startswith("runtime-core@")


def test_get_logger_returns_structlog_logger() -> None:
    logger = get_logger("runtime_core.test", component="m0")
    assert hasattr(logger, "info")
    assert hasattr(logger, "bind")
