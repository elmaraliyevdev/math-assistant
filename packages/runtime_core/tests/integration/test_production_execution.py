"""Production path resolution and execution without tests/golden layout."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from runtime_core.common.golden import load_golden_game_version
from runtime_core.common.paths import clear_schema_path_caches, resolve_game_schema_root
from runtime_core.mathematical.report import build_mathematics_report
from runtime_core.runtime.executor import SessionExecutor
from runtime_core.simulation.models import SimulationProfile
from runtime_core.simulation.runner import run_simulation
from tests.integration.helpers import (
    game_schema_root,
    golden_game_path,
    repo_root,
    run_simulation_subprocess,
)


@pytest.fixture
def isolated_schema_tree(tmp_path: Path) -> Path:
    """Copy game-schema into a temp tree that has no tests/golden manifest."""
    destination = tmp_path / "packages" / "game-schema"
    shutil.copytree(game_schema_root(), destination)
    assert not (tmp_path / "tests" / "golden" / "manifest.yaml").exists()
    return destination


@pytest.fixture
def isolated_game_json(tmp_path: Path) -> Path:
    game_path = tmp_path / "game.canonical.json"
    shutil.copyfile(golden_game_path(), game_path)
    return game_path


def test_resolve_game_schema_root_without_golden_manifest(
    isolated_schema_tree: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_schema_path_caches()
    monkeypatch.delenv("MATH_ASSISTANT_SCHEMA_ROOT", raising=False)
    resolved = resolve_game_schema_root(schema_root=isolated_schema_tree)
    assert resolved == isolated_schema_tree


def test_session_executor_without_repo_root(
    isolated_schema_tree: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MATH_ASSISTANT_SCHEMA_ROOT", str(isolated_schema_tree))
    SessionExecutor()


def test_run_simulation_without_repo_root(
    isolated_schema_tree: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MATH_ASSISTANT_SCHEMA_ROOT", str(isolated_schema_tree))
    game = load_golden_game_version(
        "fixture-01-base-5x3",
        repo_root=repo_root(),
    )
    profile = SimulationProfile.model_validate(
        {
            "spinCount": 5,
            "shardCount": 1,
            "masterSeed": "prod-path-test",
            "simulationRunId": "prod-path-test",
            "betMinorUnits": 100,
        },
    )
    result = run_simulation(game, profile, max_workers=1)
    assert result.spin_count == 5


def test_build_mathematics_report_without_repo_root(
    isolated_schema_tree: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MATH_ASSISTANT_SCHEMA_ROOT", str(isolated_schema_tree))
    game = load_golden_game_version(
        "fixture-01-base-5x3",
        repo_root=repo_root(),
    )
    profile = SimulationProfile.model_validate(
        {
            "spinCount": 3,
            "shardCount": 1,
            "masterSeed": "math-report-test",
            "simulationRunId": "math-report-test",
        },
    )
    result = run_simulation(game, profile, max_workers=1)
    report = build_mathematics_report(result, spin_wins_minor_units=(0, 0, 0))
    assert report.spin_count == 3


def test_execute_simulation_from_packages_api_cwd(
    isolated_schema_tree: Path,
    isolated_game_json: Path,
) -> None:
    completed = run_simulation_subprocess(
        cwd=repo_root() / "packages" / "api",
        schema_root=isolated_schema_tree,
        game_json=isolated_game_json,
    )
    assert completed.returncode == 0, completed.stderr
    assert "ok" in completed.stdout


def test_execute_simulation_from_repository_root_cwd(
    isolated_schema_tree: Path,
    isolated_game_json: Path,
) -> None:
    completed = run_simulation_subprocess(
        cwd=repo_root(),
        schema_root=isolated_schema_tree,
        game_json=isolated_game_json,
    )
    assert completed.returncode == 0, completed.stderr
    assert "ok" in completed.stdout


def test_execute_simulation_after_pip_install(
    isolated_schema_tree: Path,
    isolated_game_json: Path,
    tmp_path: Path,
) -> None:
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(dist_dir)],
        cwd=repo_root() / "packages" / "runtime_core",
        check=True,
    )

    wheels = list(dist_dir.glob("runtime_core-*.whl"))
    assert wheels

    venv_dir = tmp_path / "venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    pip = venv_dir / "bin" / "pip"
    python = venv_dir / "bin" / "python"
    subprocess.run([str(pip), "install", str(wheels[0])], check=True)

    empty_cwd = tmp_path / "empty"
    empty_cwd.mkdir()
    completed = run_simulation_subprocess(
        cwd=empty_cwd,
        schema_root=isolated_schema_tree,
        game_json=isolated_game_json,
        python=str(python),
    )
    assert completed.returncode == 0, completed.stderr
    assert "ok" in completed.stdout
