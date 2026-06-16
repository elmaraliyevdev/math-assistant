"""Schema path resolution for validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from runtime_core.common.paths import find_repo_root, resolve_game_schema_root


@dataclass(frozen=True, slots=True)
class SchemaPaths:
    game_schema: Path
    plugin_schema_dir: Path


def default_schema_paths(*, repo_root: Path | None = None) -> SchemaPaths:
    """Resolve canonical JSON Schema locations for production validation."""
    if repo_root is not None:
        root = resolve_game_schema_root(
            schema_root=repo_root / "packages" / "game-schema",
        )
    else:
        root = resolve_game_schema_root()
    return SchemaPaths(
        game_schema=root / "schemas" / "game-version-1.0.0.schema.json",
        plugin_schema_dir=root / "schemas" / "plugins",
    )


def schema_registry_root(*, repo_root: Path | None = None) -> Path:
    if repo_root is not None:
        return resolve_game_schema_root(schema_root=repo_root / "packages" / "game-schema")
    return resolve_game_schema_root()
