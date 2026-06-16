"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

from collections.abc import Callable
from pathlib import Path

import pytest

from runtime_core.common.golden import load_golden_game_version
from runtime_core.common.logging import configure_logging
from runtime_core.common.paths import find_repo_root, golden_fixtures_root
from runtime_core.domain.game_version import GameVersion


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Monorepo root path."""
    return find_repo_root()


@pytest.fixture(scope="session")
def golden_root(repo_root: Path) -> Path:
    """``tests/golden/`` directory."""
    return golden_fixtures_root(repo_root=repo_root)


@pytest.fixture(scope="session", autouse=True)
def _configure_test_logging() -> None:
    """Use structured logging during the test session."""
    configure_logging(json_logs=False)


@pytest.fixture
def load_golden(repo_root: Path) -> Callable[[str], GameVersion]:
    """Load a golden fixture by directory name (e.g. ``fixture-01-base-5x3``)."""

    def _load(fixture_id: str) -> GameVersion:
        return load_golden_game_version(fixture_id, repo_root=repo_root)

    return _load
