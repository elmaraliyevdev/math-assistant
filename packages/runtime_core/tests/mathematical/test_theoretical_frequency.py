"""Theoretical feature frequency tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from runtime_core.common.golden import load_golden_fixture_json
from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical.theoretical_frequency import (
    collect_trigger_specs,
    expected_feature_frequencies,
    expected_trigger_frequency,
    probability_at_least_k_reels,
    probability_reel_shows_symbol,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def test_probability_reel_shows_symbol() -> None:
    strip = ["A", "B", "SCATTER", "C", "D"]
    prob = probability_reel_shows_symbol(strip, "SCATTER", window_rows=3)
    assert prob == pytest.approx(3 / 5)


def test_probability_at_least_k_reels() -> None:
    reel_probs = [0.6, 0.6, 0.6, 0.6, 0.6]
    assert probability_at_least_k_reels(reel_probs, 3) == pytest.approx(0.68256, abs=0.0001)


def test_fixture_free_spins_expected_frequency() -> None:
    payload = load_golden_fixture_json("fixture-02-base-free-spins", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    specs = collect_trigger_specs(game)
    fs_specs = [spec for spec in specs if spec.feature == "FREE_SPINS"]
    assert fs_specs
    expected = expected_trigger_frequency(game, fs_specs[0])
    assert expected == pytest.approx(0.68256, abs=0.001)

    frequencies = expected_feature_frequencies(game)
    assert "FREE_SPINS" in frequencies
    assert frequencies["FREE_SPINS"] == pytest.approx(0.68256, abs=0.001)
