"""Feature frequency validation tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from runtime_core.common.golden import load_golden_fixture_json
from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical.feature_validation import validate_feature_frequencies
from runtime_core.simulation.models import SimulationResult


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def test_feature_validation_passes_near_theory() -> None:
    payload = load_golden_fixture_json("fixture-02-base-free-spins", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    spin_count = 10_000
    expected = 0.683
    result = SimulationResult(
        spinCount=spin_count,
        shardCount=1,
        elapsedTimeMs=1,
        totalBetMinorUnits=spin_count * 100,
        totalWinMinorUnits=spin_count * 96,
        uncappedWinMinorUnits=spin_count * 96,
        exposureTruncationCount=0,
        exposureTruncatedMinorUnits=0,
        chainFaultCount=0,
        limitHitCount=0,
        featureTriggerCounts={"FREE_SPINS": int(spin_count * expected)},
        jackpotCounts={},
        eventSampleCount=0,
        engineVersion="runtime-core@1.8.0",
    )
    validations = validate_feature_frequencies(result, game, tolerance=0.05)
    fs = next(item for item in validations if item.feature == "FREE_SPINS")
    assert fs.status == "PASS"
    assert fs.observed_frequency == pytest.approx(expected, abs=0.001)
    assert fs.expected_frequency == pytest.approx(expected, abs=0.05)


def test_feature_validation_fails_outside_tolerance() -> None:
    payload = load_golden_fixture_json("fixture-02-base-free-spins", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    result = SimulationResult(
        spinCount=1000,
        shardCount=1,
        elapsedTimeMs=1,
        totalBetMinorUnits=100_000,
        totalWinMinorUnits=96_000,
        uncappedWinMinorUnits=96_000,
        exposureTruncationCount=0,
        exposureTruncatedMinorUnits=0,
        chainFaultCount=0,
        limitHitCount=0,
        featureTriggerCounts={"FREE_SPINS": 100},
        jackpotCounts={},
        eventSampleCount=0,
        engineVersion="runtime-core@1.8.0",
    )
    validations = validate_feature_frequencies(result, game, tolerance=0.05)
    fs = next(item for item in validations if item.feature == "FREE_SPINS")
    assert fs.status == "FAIL"
