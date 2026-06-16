"""Shared utilities: paths, logging, engine metadata."""

from runtime_core.common.golden import (
    GoldenFixtureError,
    list_golden_fixtures,
    load_golden_fixture_json,
)
from runtime_core.common.logging import configure_logging
from runtime_core.common.paths import (
    find_repo_root,
    game_schema_root,
    golden_fixtures_root,
    resolve_game_schema_root,
)
from runtime_core.common.version import ENGINE_VERSION

__all__ = [
    "ENGINE_VERSION",
    "GoldenFixtureError",
    "configure_logging",
    "find_repo_root",
    "game_schema_root",
    "golden_fixtures_root",
    "resolve_game_schema_root",
    "list_golden_fixtures",
    "load_golden_fixture_json",
]
