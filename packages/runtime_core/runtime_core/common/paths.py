"""Path resolution for game schemas (production) and golden fixtures (tests only)."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

_GOLDEN_MANIFEST = "tests/golden/manifest.yaml"
_GAME_SCHEMA_PACKAGE_REL = "packages/game-schema"
_SCHEMA_MARKER = Path("schemas") / "game-version-1.0.0.schema.json"
_BUNDLED_SCHEMA_REL = Path("data") / "game-schema"


def _is_valid_schema_root(root: Path) -> bool:
    return (root / _SCHEMA_MARKER).is_file()


def clear_schema_path_caches() -> None:
    """Reset cached bundled schema resolution (for tests)."""
    _bundled_game_schema_root.cache_clear()


def resolve_game_schema_root(*, schema_root: Path | None = None) -> Path:
    """Resolve ``game-schema`` for runtime execution without requiring ``tests/``.

    Resolution order:
    1. Explicit *schema_root*
    2. ``MATH_ASSISTANT_SCHEMA_ROOT`` environment variable
    3. Bundled wheel data under ``runtime_core/data/game-schema``
    4. Monorepo layout: walk upward for ``packages/game-schema``
    """
    if schema_root is not None:
        if not _is_valid_schema_root(schema_root):
            msg = f"invalid game schema root: {schema_root}"
            raise FileNotFoundError(msg)
        return schema_root

    env_root = os.environ.get("MATH_ASSISTANT_SCHEMA_ROOT")
    if env_root:
        candidate = Path(env_root)
        if _is_valid_schema_root(candidate):
            return candidate
        msg = (
            "MATH_ASSISTANT_SCHEMA_ROOT does not contain "
            f"{_SCHEMA_MARKER.as_posix()}: {candidate}"
        )
        raise FileNotFoundError(msg)

    bundled = _bundled_game_schema_root()
    if bundled is not None:
        return bundled

    monorepo = _find_monorepo_game_schema_root()
    if monorepo is not None:
        return monorepo

    msg = (
        "game schema root not found; set MATH_ASSISTANT_SCHEMA_ROOT, install "
        "runtime-core with bundled schema data, or run from the monorepo checkout"
    )
    raise FileNotFoundError(msg)


@lru_cache(maxsize=1)
def _bundled_game_schema_root() -> Path | None:
    package_root = Path(__file__).resolve().parent.parent
    candidate = package_root / _BUNDLED_SCHEMA_REL
    return candidate if _is_valid_schema_root(candidate) else None


def _find_monorepo_game_schema_root(*, start: Path | None = None) -> Path | None:
    current = (start or Path(__file__)).resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        schema_root = candidate / _GAME_SCHEMA_PACKAGE_REL
        if _is_valid_schema_root(schema_root):
            return schema_root
    return None


def find_repo_root(*, start: Path | None = None) -> Path:
    """Return the monorepo root containing golden fixtures (tests/certification only)."""
    current = (start or Path(__file__)).resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / _GOLDEN_MANIFEST).is_file():
            return candidate
    msg = f"repository root not found (missing {_GOLDEN_MANIFEST})"
    raise FileNotFoundError(msg)


def golden_fixtures_root(*, repo_root: Path | None = None) -> Path:
    """Path to ``tests/golden/`` (tests and golden_runner only)."""
    root = repo_root or find_repo_root()
    return root / "tests" / "golden"


def game_schema_root(*, repo_root: Path | None = None) -> Path:
    """Resolve ``packages/game-schema`` for backward-compatible call sites."""
    if repo_root is not None:
        candidate = repo_root / _GAME_SCHEMA_PACKAGE_REL
        if not _is_valid_schema_root(candidate):
            schema_file = candidate / _SCHEMA_MARKER
            msg = f"game schema not found at {schema_file}"
            raise FileNotFoundError(msg)
        return candidate
    return resolve_game_schema_root()
