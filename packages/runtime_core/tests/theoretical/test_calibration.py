"""Calibration and recommendation engine tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from runtime_core.common.golden import load_golden_fixture_json
from runtime_core.domain.game_version import GameVersion
from runtime_core.theoretical.calibration import (
    calibrate_rtp,
    generate_calibration_recommendations,
)
from runtime_core.theoretical.theoretical_features import calculate_feature_probabilities
from runtime_core.theoretical.theoretical_rtp import calculate_theoretical_rtp


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def test_calibrate_within_tolerance() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    theoretical = calculate_theoretical_rtp(game)
    calibration = calibrate_rtp(
        theoretical_rtp=theoretical,
        simulated_rtp=0.0512,
        target_rtp=5.12,
        tolerance=0.5,
    )
    assert calibration.theoretical_rtp == pytest.approx(5.12, abs=0.01)
    assert calibration.simulated_rtp == pytest.approx(5.12, abs=0.01)
    assert calibration.within_tolerance is True


def test_calibrate_theory_vs_simulation_delta() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    theoretical = calculate_theoretical_rtp(game)
    calibration = calibrate_rtp(
        theoretical_rtp=theoretical,
        simulated_rtp=0.07,
        target_rtp=96.0,
        tolerance=0.1,
    )
    assert calibration.theory_vs_simulation_delta == pytest.approx(1.88, abs=0.05)
    assert calibration.within_tolerance is False


def test_recommendations_when_above_target() -> None:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    theoretical = calculate_theoretical_rtp(game)
    features = calculate_feature_probabilities(game)
    calibration = calibrate_rtp(
        theoretical_rtp=theoretical,
        target_rtp=1.0,
        tolerance=0.1,
    )
    recommendations = generate_calibration_recommendations(
        game,
        calibration,
        theoretical,
        features,
    )
    assert recommendations
    assert any("Increase" in rec.action or "Reduce" in rec.action for rec in recommendations)
    assert all(rec.expected_rtp_impact for rec in recommendations)
