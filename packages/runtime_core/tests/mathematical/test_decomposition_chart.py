"""RTP decomposition chart tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from runtime_core.common.golden import load_golden_fixture_json
from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical.decomposition_chart import build_rtp_decomposition_chart
from runtime_core.simulation.models import SimulationResult


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def test_decomposition_chart_sums_to_total_rtp() -> None:
    payload = load_golden_fixture_json("fixture-04-nested-fs-hold-win", repo_root=_repo_root())
    game = GameVersion.model_validate(payload)
    result = SimulationResult(
        spinCount=10_000,
        shardCount=1,
        elapsedTimeMs=1,
        totalBetMinorUnits=1_000_000,
        totalWinMinorUnits=510_000,
        uncappedWinMinorUnits=510_000,
        exposureTruncationCount=0,
        exposureTruncatedMinorUnits=0,
        chainFaultCount=0,
        limitHitCount=0,
        featureTriggerCounts={"FREE_SPINS": 6840},
        jackpotCounts={},
        winByRtpCategoryMinorUnits={
            "BASE": 50_000,
            "FREE_SPINS": 460_000,
            "HOLD_AND_WIN": 0,
        },
        nestedFeatureEntries=0,
        eventSampleCount=0,
        engineVersion="runtime-core@1.8.0",
    )

    chart = build_rtp_decomposition_chart(result, game)
    parts = chart.base + chart.free_spins + chart.hold_and_win + chart.jackpot
    assert parts == pytest.approx(chart.total_rtp, abs=0.01)
    assert chart.total_rtp == pytest.approx(51.0, abs=0.01)
    assert chart.base == pytest.approx(5.0, abs=0.01)
    assert chart.free_spins == pytest.approx(46.0, abs=0.01)


def test_decomposition_chart_empty_bet() -> None:
    result = SimulationResult(
        spinCount=0,
        shardCount=1,
        elapsedTimeMs=0,
        totalBetMinorUnits=0,
        totalWinMinorUnits=0,
        uncappedWinMinorUnits=0,
        exposureTruncationCount=0,
        exposureTruncatedMinorUnits=0,
        chainFaultCount=0,
        limitHitCount=0,
        featureTriggerCounts={},
        jackpotCounts={},
        eventSampleCount=0,
        engineVersion="runtime-core@1.8.0",
    )
    chart = build_rtp_decomposition_chart(result)
    assert chart.total_rtp == 0.0
