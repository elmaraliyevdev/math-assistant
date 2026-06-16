"""Helpers for production-path integration tests."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
_GAME_SCHEMA_ROOT = _REPO_ROOT / "packages" / "game-schema"
_GOLDEN_GAME = _REPO_ROOT / "tests" / "golden" / "fixture-01-base-5x3" / "game.canonical.json"

_SIMULATION_SCRIPT = """
import json
import os
from pathlib import Path

from runtime_core.domain.game_version import GameVersion
from runtime_core.runtime.executor import SessionExecutor
from runtime_core.simulation.models import SimulationProfile
from runtime_core.simulation.runner import run_simulation

schema_root = os.environ.get("MATH_ASSISTANT_SCHEMA_ROOT")
if schema_root:
    os.environ["MATH_ASSISTANT_SCHEMA_ROOT"] = schema_root

game_path = Path(os.environ["GAME_JSON_PATH"])
game = GameVersion.model_validate(json.loads(game_path.read_text(encoding="utf-8")))
profile = SimulationProfile.model_validate(
    {
        "spinCount": 5,
        "shardCount": 1,
        "masterSeed": "prod-path-test",
        "simulationRunId": "prod-path-test",
        "betMinorUnits": 100,
    },
)

SessionExecutor()
result = run_simulation(game, profile, max_workers=1)
assert result.spin_count == 5
print("ok")
"""


def run_simulation_subprocess(
    *,
    cwd: Path,
    schema_root: Path,
    game_json: Path,
    python: str | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["MATH_ASSISTANT_SCHEMA_ROOT"] = str(schema_root)
    env["GAME_JSON_PATH"] = str(game_json)
    env["PYTHONUNBUFFERED"] = "1"
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [python or sys.executable, "-c", _SIMULATION_SCRIPT],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def repo_root() -> Path:
    return _REPO_ROOT


def game_schema_root() -> Path:
    return _GAME_SCHEMA_ROOT


def golden_game_path() -> Path:
    return _GOLDEN_GAME
