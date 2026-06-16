"""Golden fixture loading utilities for regression tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from runtime_core.common.paths import golden_fixtures_root
from runtime_core.domain.game_version import GameVersion


class GoldenFixtureError(Exception):
    """Raised when a golden fixture cannot be loaded or parsed."""


def list_golden_fixtures(*, repo_root: Path | None = None) -> list[str]:
    """Return sorted fixture directory names under ``tests/golden/``."""
    root = golden_fixtures_root(repo_root=repo_root)
    return sorted(
        path.name
        for path in root.iterdir()
        if path.is_dir() and (path / "game.canonical.json").is_file()
    )


def golden_fixture_path(fixture_id: str, *, repo_root: Path | None = None) -> Path:
    """Resolve ``tests/golden/{fixture_id}/game.canonical.json``."""
    if not fixture_id or "/" in fixture_id or fixture_id.startswith("."):
        msg = f"invalid golden fixture id: {fixture_id!r}"
        raise GoldenFixtureError(msg)
    root = golden_fixtures_root(repo_root=repo_root)
    path = root / fixture_id / "game.canonical.json"
    if not path.is_file():
        msg = f"golden fixture not found: {path}"
        raise GoldenFixtureError(msg)
    return path


def load_golden_fixture_json(
    fixture_id: str,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Load a golden fixture as parsed JSON."""
    path = golden_fixture_path(fixture_id, repo_root=repo_root)
    try:
        raw: object = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        msg = f"invalid JSON in golden fixture {fixture_id}: {exc}"
        raise GoldenFixtureError(msg) from exc
    if not isinstance(raw, dict):
        msg = f"golden fixture {fixture_id} root must be a JSON object"
        raise GoldenFixtureError(msg)
    return cast("dict[str, Any]", raw)


def load_golden_game_version(
    fixture_id: str,
    *,
    repo_root: Path | None = None,
) -> GameVersion:
    """Load and parse a golden fixture into a :class:`GameVersion`."""
    payload = load_golden_fixture_json(fixture_id, repo_root=repo_root)
    try:
        return GameVersion.model_validate(payload)
    except Exception as exc:
        msg = f"failed to parse golden fixture {fixture_id} as GameVersion: {exc}"
        raise GoldenFixtureError(msg) from exc
