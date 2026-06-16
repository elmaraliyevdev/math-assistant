"""RTP target validation tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from runtime_core.common.golden import load_golden_fixture_json
from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical.rtp_validation import validate_rtp_target
from runtime_core.simulation.models import SimulationResult

from tests.mathematical.conftest import sample_simulation_result


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


@pytest.fixture
def game_with_rtp_target() -> GameVersion:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    return GameVersion.model_validate(payload)


def test_validate_rtp_target_within_tolerance(game_with_rtp_target: GameVersion) -> None:
    result = sample_simulation_result(
        spin_count=1000,
        total_bet=100_000,
        total_win=95_910,
        uncapped_win=95_910,
    )
    validation = validate_rtp_target(
        result,
        game_with_rtp_target,
        actual_rtp_ratio=0.9591,
    )
    assert validation is not None
    assert validation.target_rtp == 96.0
    assert validation.actual_rtp == pytest.approx(95.91)
    assert validation.difference == pytest.approx(-0.09)
    assert validation.tolerance == 0.1
    assert validation.within_tolerance is True


def test_validate_rtp_target_outside_tolerance(game_with_rtp_target: GameVersion) -> None:
    result = sample_simulation_result(
        spin_count=1000,
        total_bet=100_000,
        total_win=90_000,
        uncapped_win=90_000,
    )
    validation = validate_rtp_target(result, game_with_rtp_target)
    assert validation is not None
    assert validation.actual_rtp == pytest.approx(90.0)
    assert validation.within_tolerance is False


def test_validate_rtp_target_missing_metadata(game_with_rtp_target: GameVersion) -> None:
    payload = game_with_rtp_target.model_dump(mode="json", by_alias=True)
    payload["metadata"] = {"title": "No RTP target"}
    game = GameVersion.model_validate(payload)
    result = sample_simulation_result()
    assert validate_rtp_target(result, game) is None
