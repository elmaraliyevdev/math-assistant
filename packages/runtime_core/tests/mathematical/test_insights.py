"""Mathematics insights orchestration tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from runtime_core.common.golden import load_golden_fixture_json
from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical.decomposition_chart import build_rtp_decomposition_chart
from runtime_core.mathematical.insights import enrich_mathematics_report
from runtime_core.mathematical.report import build_mathematics_report
from runtime_core.simulation.models import SimulationResult

from tests.mathematical.conftest import SAMPLE_SPIN_WINS, sample_simulation_result


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _game(name: str) -> GameVersion:
    payload = load_golden_fixture_json(name, repo_root=_repo_root())
    return GameVersion.model_validate(payload)


def test_enrich_mathematics_report_attaches_insights() -> None:
    game = _game("fixture-02-base-free-spins")
    result = sample_simulation_result(
        spin_count=4,
        total_bet=400,
        total_win=380,
        uncapped_win=380,
        feature_triggers={"FREE_SPINS": 3},
    )
    result = result.model_copy(
        update={
            "win_by_rtp_category_minor_units": {"BASE": 100, "FREE_SPINS": 280},
        },
    )
    base = build_mathematics_report(result, spin_wins_minor_units=SAMPLE_SPIN_WINS)
    enriched = enrich_mathematics_report(base, game=game, result=result)

    assert enriched.rtp_validation is not None
    assert enriched.rtp_decomposition_chart.total_rtp > 0
    assert enriched.feature_validation
    assert isinstance(enriched.recommendations, tuple)


def test_build_mathematics_report_with_game_includes_insights() -> None:
    game = _game("fixture-01-base-5x3")
    result = sample_simulation_result(
        spin_count=4,
        total_bet=400,
        total_win=384,
        uncapped_win=384,
    )
    report = build_mathematics_report(
        result,
        spin_wins_minor_units=SAMPLE_SPIN_WINS,
        game=game,
    )
    assert report.rtp_validation is not None
    assert report.rtp_validation.target_rtp == 96.0


def test_decomposition_chart_jackpot_split() -> None:
    game = _game("fixture-04-nested-fs-hold-win")
    result = SimulationResult(
        spinCount=1000,
        shardCount=1,
        elapsedTimeMs=1,
        totalBetMinorUnits=100_000,
        totalWinMinorUnits=200_000,
        uncappedWinMinorUnits=200_000,
        exposureTruncationCount=0,
        exposureTruncatedMinorUnits=0,
        chainFaultCount=0,
        limitHitCount=0,
        featureTriggerCounts={"HOLD_AND_WIN": 5},
        jackpotCounts={"MINI": 2, "MAJOR": 1},
        winByRtpCategoryMinorUnits={"BASE": 10_000, "FREE_SPINS": 50_000, "HOLD_AND_WIN": 140_000},
        nestedFeatureEntries=0,
        eventSampleCount=0,
        engineVersion="runtime-core@1.8.0",
    )
    chart = build_rtp_decomposition_chart(result, game)
    parts = chart.base + chart.free_spins + chart.hold_and_win + chart.jackpot
    assert parts == pytest.approx(chart.total_rtp, abs=0.05)
    assert chart.jackpot >= 0
