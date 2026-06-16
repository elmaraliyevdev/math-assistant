"""Recommendation engine tests."""

from __future__ import annotations

from pathlib import Path

from runtime_core.common.golden import load_golden_fixture_json
from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical.models import RtpValidationResult
from runtime_core.mathematical.recommendations import generate_recommendations
from runtime_core.simulation.models import SimulationResult


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _game() -> GameVersion:
    payload = load_golden_fixture_json("fixture-04-nested-fs-hold-win", repo_root=_repo_root())
    return GameVersion.model_validate(payload)


def test_recommendation_low_base_rtp() -> None:
    result = SimulationResult(
        spinCount=1000,
        shardCount=1,
        elapsedTimeMs=1,
        totalBetMinorUnits=100_000,
        totalWinMinorUnits=52_000,
        uncappedWinMinorUnits=52_000,
        exposureTruncationCount=0,
        exposureTruncatedMinorUnits=0,
        chainFaultCount=0,
        limitHitCount=0,
        featureTriggerCounts={"FREE_SPINS": 100},
        jackpotCounts={},
        winByRtpCategoryMinorUnits={"BASE": 5_200, "FREE_SPINS": 46_800},
        nestedFeatureEntries=0,
        eventSampleCount=0,
        engineVersion="runtime-core@1.8.0",
    )
    recommendations = generate_recommendations(result, _game())
    titles = {item.title for item in recommendations}
    assert "Low Base RTP" in titles


def test_recommendation_rtp_below_target() -> None:
    result = SimulationResult(
        spinCount=1000,
        shardCount=1,
        elapsedTimeMs=1,
        totalBetMinorUnits=100_000,
        totalWinMinorUnits=90_000,
        uncappedWinMinorUnits=90_000,
        exposureTruncationCount=0,
        exposureTruncatedMinorUnits=0,
        chainFaultCount=0,
        limitHitCount=0,
        featureTriggerCounts={},
        jackpotCounts={},
        winByRtpCategoryMinorUnits={"BASE": 90_000},
        nestedFeatureEntries=0,
        eventSampleCount=0,
        engineVersion="runtime-core@1.8.0",
    )
    rtp_validation = RtpValidationResult(
        targetRtp=96.0,
        actualRtp=90.0,
        difference=-6.0,
        tolerance=0.1,
        withinTolerance=False,
    )
    recommendations = generate_recommendations(
        result,
        _game(),
        rtp_validation=rtp_validation,
    )
    assert any(item.title == "RTP Below Target" for item in recommendations)


def test_recommendation_high_free_spins_share() -> None:
    result = SimulationResult(
        spinCount=1000,
        shardCount=1,
        elapsedTimeMs=1,
        totalBetMinorUnits=100_000,
        totalWinMinorUnits=80_000,
        uncappedWinMinorUnits=80_000,
        exposureTruncationCount=0,
        exposureTruncatedMinorUnits=0,
        chainFaultCount=0,
        limitHitCount=0,
        featureTriggerCounts={"FREE_SPINS": 100},
        jackpotCounts={},
        winByRtpCategoryMinorUnits={"BASE": 5_000, "FREE_SPINS": 75_000},
        nestedFeatureEntries=0,
        eventSampleCount=0,
        engineVersion="runtime-core@1.8.0",
    )
    recommendations = generate_recommendations(result, _game())
    assert any(item.title == "High Free Spins RTP Share" for item in recommendations)


def test_recommendation_hold_and_win_not_contributing() -> None:
    result = SimulationResult(
        spinCount=1000,
        shardCount=1,
        elapsedTimeMs=1,
        totalBetMinorUnits=100_000,
        totalWinMinorUnits=50_000,
        uncappedWinMinorUnits=50_000,
        exposureTruncationCount=0,
        exposureTruncatedMinorUnits=0,
        chainFaultCount=0,
        limitHitCount=0,
        featureTriggerCounts={},
        jackpotCounts={},
        winByRtpCategoryMinorUnits={"BASE": 50_000},
        nestedFeatureEntries=0,
        eventSampleCount=0,
        engineVersion="runtime-core@1.8.0",
    )
    recommendations = generate_recommendations(result, _game())
    assert any(item.title == "Hold & Win Not Contributing" for item in recommendations)


def test_recommendation_high_feature_frequency() -> None:
    result = SimulationResult(
        spinCount=100,
        shardCount=1,
        elapsedTimeMs=1,
        totalBetMinorUnits=10_000,
        totalWinMinorUnits=5_000,
        uncappedWinMinorUnits=5_000,
        exposureTruncationCount=0,
        exposureTruncatedMinorUnits=0,
        chainFaultCount=0,
        limitHitCount=0,
        featureTriggerCounts={"FREE_SPINS": 60},
        jackpotCounts={},
        winByRtpCategoryMinorUnits={"BASE": 1_000, "FREE_SPINS": 4_000},
        nestedFeatureEntries=0,
        eventSampleCount=0,
        engineVersion="runtime-core@1.8.0",
    )
    recommendations = generate_recommendations(result, _game())
    assert any(item.title == "High Feature Frequency" for item in recommendations)
