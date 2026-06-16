"""Loader error-path tests for golden artifacts."""

from __future__ import annotations

from pathlib import Path

import pytest

from runtime_core.golden.loader import (
    GoldenArtifactError,
    golden_fixture_dir,
    load_expected_baseline,
    load_manifest,
    load_simulation_profile,
    list_manifest_fixtures,
)


def test_golden_fixture_dir_missing(tmp_path: Path) -> None:
    with pytest.raises(GoldenArtifactError, match="not found"):
        golden_fixture_dir("fixture-01-base-5x3", repo_root=tmp_path)


def test_load_manifest_missing(tmp_path: Path) -> None:
    with pytest.raises(GoldenArtifactError, match="not found"):
        load_manifest(repo_root=tmp_path)


def test_load_manifest_invalid_fixtures(tmp_path: Path) -> None:
    golden_dir = tmp_path / "tests" / "golden"
    golden_dir.mkdir(parents=True)
    (golden_dir / "manifest.yaml").write_text("fixtures: not-a-list\n", encoding="utf-8")
    with pytest.raises(GoldenArtifactError, match="fixtures must be a list"):
        list_manifest_fixtures(repo_root=tmp_path)


def test_load_simulation_profile_invalid_yaml(tmp_path: Path) -> None:
    fixture_dir = tmp_path / "tests" / "golden" / "fixture-x"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "simulation.profile.yaml").write_text(":\n- bad\n", encoding="utf-8")
    with pytest.raises(GoldenArtifactError, match="invalid YAML"):
        load_simulation_profile("fixture-x", repo_root=tmp_path)


def test_load_simulation_profile_invalid_schema(tmp_path: Path) -> None:
    fixture_dir = tmp_path / "tests" / "golden" / "fixture-x"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "simulation.profile.yaml").write_text("profileVersion: x\n", encoding="utf-8")
    with pytest.raises(GoldenArtifactError, match="failed to parse simulation profile"):
        load_simulation_profile("fixture-x", repo_root=tmp_path)


def test_load_expected_baseline_invalid_root(tmp_path: Path) -> None:
    fixture_dir = tmp_path / "tests" / "golden" / "fixture-x"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "expected.yaml").write_text("[]\n", encoding="utf-8")
    with pytest.raises(GoldenArtifactError, match="must be a mapping"):
        load_expected_baseline("fixture-x", repo_root=tmp_path)


def test_load_expected_baseline_invalid_schema(tmp_path: Path) -> None:
    fixture_dir = tmp_path / "tests" / "golden" / "fixture-x"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "expected.yaml").write_text("version: x\n", encoding="utf-8")
    with pytest.raises(GoldenArtifactError, match="failed to parse expected baseline"):
        load_expected_baseline("fixture-x", repo_root=tmp_path)


def test_invalid_fixture_id() -> None:
    from runtime_core.common.golden import golden_fixture_path

    with pytest.raises(Exception, match="invalid golden fixture id"):
        golden_fixture_path("../escape")
