"""Theoretical feature probability tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from runtime_core.common.golden import load_golden_fixture_json
from runtime_core.domain.game_version import GameVersion
from runtime_core.theoretical.theoretical_features import calculate_feature_probabilities


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def test_free_spins_probability_fixture_02() -> None:
    payload = load_golden_fixture_json("fixture-02-base-free-spins", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    probabilities = calculate_feature_probabilities(game)
    fs = next(item for item in probabilities if item.trigger == "FREE_SPINS")
    assert fs.probability > 0.0
    assert fs.one_in_x is not None
    assert fs.one_in_x > 1.0


def test_hold_and_win_and_jackpot_probabilities_fixture_03() -> None:
    payload = load_golden_fixture_json("fixture-03-base-hold-win", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    probabilities = calculate_feature_probabilities(game)
    triggers = {item.trigger for item in probabilities}
    assert "HOLD_AND_WIN" in triggers
    assert any(item.startswith("JACKPOT_") for item in triggers)


def test_one_in_x_matches_probability() -> None:
    payload = load_golden_fixture_json("fixture-02-base-free-spins", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    for item in calculate_feature_probabilities(game):
        if item.probability > 0:
            assert item.one_in_x == pytest.approx(round(1.0 / item.probability, 2))
