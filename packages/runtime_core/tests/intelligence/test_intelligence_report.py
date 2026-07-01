"""Tests for simulation intelligence module."""

from __future__ import annotations

from pathlib import Path

from runtime_core.common.golden import load_golden_fixture_json
from runtime_core.domain.game_version import GameVersion
from runtime_core.intelligence.collector import IntelligenceCollector
from runtime_core.intelligence.evidence import confidence_from_sample_size
from runtime_core.intelligence.models import IntelligenceSnapshot
from runtime_core.intelligence.report import build_simulation_intelligence_report
from runtime_core.mathematical.insights import enrich_mathematics_report
from runtime_core.mathematical.report import build_mathematics_report
from runtime_core.simulation.models import SimulationResult
from tests.mathematical.conftest import SAMPLE_SPIN_WINS, sample_simulation_result


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _load_game() -> GameVersion:
    payload = load_golden_fixture_json("fixture-01-base-5x3", repo_root=_repo_root())
    return GameVersion.model_validate(payload)


def test_intelligence_snapshot_merge_is_commutative() -> None:
    left = IntelligenceSnapshot(
        grid_observation_count=2,
        symbol_occurrence_counts={"A": 3},
        scatter_landings_by_reel={"0": 1},
    )
    right = IntelligenceSnapshot(
        grid_observation_count=1,
        symbol_occurrence_counts={"A": 2, "B": 1},
        scatter_landings_by_reel={"1": 2},
    )
    assert left.merge(right).grid_observation_count == 3
    assert left.merge(right).symbol_occurrence_counts["A"] == 5


def test_collector_records_grid_and_wins() -> None:
    collector = IntelligenceCollector()
    collector.record_grid(
        "BASE",
        [["A", "S"], ["K", "A"], ["S", "A"]],
    )
    collector.record_wins(
        [
            {"symbolId": "A", "winMinorUnits": 100, "count": 3, "source": "line"},
            {"symbolId": "K", "winMinorUnits": 50, "count": 2, "source": "line"},
        ],
    )
    snapshot = collector.freeze()
    assert snapshot.grid_observation_count == 1
    assert snapshot.symbol_occurrence_counts["S"] == 2
    assert snapshot.symbol_win_minor_units["A"] == 100
    assert snapshot.scatter_count_histogram["2"] == 1


def test_confidence_from_sample_size() -> None:
    confidence = confidence_from_sample_size(0.2, 0.2, sample_size=1_000_000)
    assert confidence.score >= 0
    assert confidence.label in {"High", "Very high", "Medium", "Low"}


def test_build_simulation_intelligence_report_from_golden() -> None:
    game = _load_game()
    result = sample_simulation_result(
        spin_count=4,
        total_bet=4000,
        total_win=7500,
        feature_triggers={"FREE_SPINS": 1},
    )
    result = result.model_copy(
        update={
            "intelligence_snapshot": IntelligenceSnapshot(
                grid_observation_count=16,
                symbol_occurrence_counts={"A": 20, "K": 12, "S": 4},
                scatter_landings_by_reel={"0": 1, "2": 3},
                wild_landings_by_reel={"1": 2},
                symbol_win_minor_units={"A": 5000, "K": 2500},
                near_miss_count=2,
            ),
        },
    )
    report = build_mathematics_report(result, spin_wins_minor_units=SAMPLE_SPIN_WINS, game=game)
    enriched = enrich_mathematics_report(report, game=game, result=result)
    intelligence = build_simulation_intelligence_report(
        result=result,
        report=enriched,
        game=game,
    )
    assert intelligence.spin_count == 4
    assert intelligence.overview
    assert intelligence.symbol_profiles
    assert intelligence.design_vs_reality
    assert intelligence.recommendations or intelligence.metric_explanations
    assert enriched.simulation_intelligence is not None


def test_enrich_mathematics_report_attaches_intelligence() -> None:
    game = _load_game()
    result = SimulationResult(
        spin_count=4,
        shard_count=1,
        elapsed_time_ms=10,
        total_bet_minor_units=4000,
        total_win_minor_units=7500,
        uncapped_win_minor_units=8000,
        exposure_truncation_count=0,
        exposure_truncated_minor_units=0,
        chain_fault_count=0,
        limit_hit_count=0,
        feature_trigger_counts={"FREE_SPINS": 1},
        jackpot_counts={},
        event_sample_count=0,
        engine_version="runtime-core@1.8.0",
        intelligence_snapshot=IntelligenceSnapshot(grid_observation_count=8),
    )
    report = build_mathematics_report(result, spin_wins_minor_units=SAMPLE_SPIN_WINS)
    enriched = enrich_mathematics_report(report, game=game, result=result)
    assert enriched.simulation_intelligence is not None
    assert enriched.simulation_intelligence.overview
