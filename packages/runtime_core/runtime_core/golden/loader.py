"""Load golden fixture runtime validation artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import yaml

from runtime_core.common.golden import GoldenFixtureError, golden_fixture_path
from runtime_core.common.paths import golden_fixtures_root
from runtime_core.golden.models import ExpectedBaseline, GoldenRuntimeProfile


class GoldenArtifactError(GoldenFixtureError):
    """Raised when golden YAML artifacts are missing or invalid."""


def golden_fixture_dir(fixture_id: str, *, repo_root: Path | None = None) -> Path:
    root = golden_fixtures_root(repo_root=repo_root)
    path = root / fixture_id
    if not path.is_dir():
        msg = f"golden fixture directory not found: {path}"
        raise GoldenArtifactError(msg)
    return path


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        msg = f"golden artifact not found: {path}"
        raise GoldenArtifactError(msg)
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        msg = f"invalid YAML in {path}: {exc}"
        raise GoldenArtifactError(msg) from exc
    if not isinstance(raw, dict):
        msg = f"golden artifact root must be a mapping: {path}"
        raise GoldenArtifactError(msg)
    return cast("dict[str, Any]", raw)


def load_simulation_profile(
    fixture_id: str,
    *,
    repo_root: Path | None = None,
) -> GoldenRuntimeProfile:
    path = golden_fixture_dir(fixture_id, repo_root=repo_root) / "simulation.profile.yaml"
    payload = _load_yaml(path)
    try:
        return GoldenRuntimeProfile.model_validate(payload)
    except Exception as exc:
        msg = f"failed to parse simulation profile for {fixture_id}: {exc}"
        raise GoldenArtifactError(msg) from exc


def load_expected_baseline(
    fixture_id: str,
    *,
    repo_root: Path | None = None,
) -> ExpectedBaseline:
    path = golden_fixture_dir(fixture_id, repo_root=repo_root) / "expected.yaml"
    payload = _load_yaml(path)
    try:
        return ExpectedBaseline.model_validate(payload)
    except Exception as exc:
        msg = f"failed to parse expected baseline for {fixture_id}: {exc}"
        raise GoldenArtifactError(msg) from exc


def load_manifest(*, repo_root: Path | None = None) -> dict[str, Any]:
    path = golden_fixtures_root(repo_root=repo_root) / "manifest.yaml"
    return _load_yaml(path)


def list_manifest_fixtures(*, repo_root: Path | None = None) -> list[str]:
    manifest = load_manifest(repo_root=repo_root)
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list):
        msg = "manifest.yaml fixtures must be a list"
        raise GoldenArtifactError(msg)
    ids: list[str] = []
    for item in fixtures:
        if not isinstance(item, dict):
            continue
        fixture_id = item.get("id")
        if isinstance(fixture_id, str):
            ids.append(fixture_id)
    return ids


def assert_fixture_game_present(fixture_id: str, *, repo_root: Path | None = None) -> Path:
    return golden_fixture_path(fixture_id, repo_root=repo_root)
