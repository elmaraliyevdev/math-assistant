"""Decomposition-aware recommendation engine tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from runtime_core.common.golden import load_golden_fixture_json
from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical.models import RtpDecompositionChart
from runtime_core.theoretical.calibration import (
    calibrate_rtp,
    generate_calibration_recommendations,
)
from runtime_core.theoretical.models import TheoreticalRtpResult
from runtime_core.theoretical.theoretical_features import calculate_feature_probabilities
from runtime_core.theoretical.theoretical_rtp import calculate_theoretical_rtp


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _game(fixture: str = "fixture-01-base-5x3") -> GameVersion:
    payload = load_golden_fixture_json(fixture, repo_root=_repo_root())
    return GameVersion.model_validate(payload)


def _theoretical_from_chart(chart: RtpDecompositionChart) -> TheoreticalRtpResult:
    return TheoreticalRtpResult(
        totalRtp=chart.total_rtp / 100.0,
        baseRtp=chart.base / 100.0,
        scatterRtp=0.0,
        lineRtp=chart.base / 100.0,
        outcomeCount=1000,
        reelSetId="base_game",
    )


def _recommendations_for_chart(
    chart: RtpDecompositionChart,
    *,
    target_rtp: float = 96.0,
    fixture: str = "fixture-01-base-5x3",
) -> tuple:
    game = _game(fixture)
    theoretical = _theoretical_from_chart(chart)
    calibration = calibrate_rtp(
        theoretical_rtp=theoretical,
        target_rtp=target_rtp,
        tolerance=0.1,
    )
    recommendations = generate_calibration_recommendations(
        game,
        calibration,
        theoretical,
        calculate_feature_probabilities(game),
        decomposition=chart,
    )
    return calibration, recommendations


def test_high_free_spins_low_base_prioritizes_base_not_scatter_reduction() -> None:
    chart = RtpDecompositionChart(
        base=5.0,
        free_spins=45.0,
        hold_and_win=0.0,
        jackpot=0.0,
        total_rtp=50.0,
    )
    _, recommendations = _recommendations_for_chart(chart)

    actions = " ".join(rec.action for rec in recommendations)
    impacts = " ".join(rec.expected_rtp_impact for rec in recommendations)

    assert any(rec.category in {"base_rtp", "paytable_redesign"} for rec in recommendations)
    assert not any(rec.category == "hold_and_win" for rec in recommendations)
    assert not any(
        rec.category == "scatter_frequency" or "reduce scatter" in rec.action.lower()
        for rec in recommendations
    )
    assert "BASE RTP is 5.00%" in impacts
    assert "expected" in impacts
    positive_impacts = [
        rec.estimated_rtp_contribution_pp
        for rec in recommendations
        if rec.estimated_rtp_contribution_pp > 0
    ]
    assert positive_impacts == sorted(positive_impacts, reverse=True)


def test_high_base_low_features_recommends_feature_tuning() -> None:
    chart = RtpDecompositionChart(
        base=82.0,
        free_spins=4.0,
        hold_and_win=1.0,
        jackpot=0.0,
        total_rtp=87.0,
    )
    _, recommendations = _recommendations_for_chart(
        chart,
        fixture="fixture-02-base-free-spins",
    )

    actions = " ".join(rec.action for rec in recommendations)
    assert any(rec.category == "feature_awards" for rec in recommendations)
    assert "FREE_SPINS" in actions


def test_excessive_jackpot_dominance_recommends_jackpot_reduction() -> None:
    chart = RtpDecompositionChart(
        base=30.0,
        free_spins=25.0,
        hold_and_win=10.0,
        jackpot=45.0,
        total_rtp=110.0,
    )
    theoretical = _theoretical_from_chart(chart)
    calibration = calibrate_rtp(
        theoretical_rtp=theoretical,
        target_rtp=96.0,
        tolerance=0.1,
    )
    recommendations = generate_calibration_recommendations(
        _game("fixture-03-base-hold-win"),
        calibration,
        theoretical,
        calculate_feature_probabilities(_game("fixture-03-base-hold-win")),
        decomposition=chart,
    )

    jackpot_recs = [rec for rec in recommendations if rec.category == "jackpot"]
    assert jackpot_recs
    assert any("JACKPOT RTP is 45.00%" in rec.expected_rtp_impact for rec in jackpot_recs)
    assert not any("Reduce scatter" in rec.action for rec in recommendations)


def test_balanced_game_near_target_has_minimal_guidance() -> None:
    chart = RtpDecompositionChart(
        base=48.0,
        free_spins=30.0,
        hold_and_win=10.0,
        jackpot=8.0,
        total_rtp=96.0,
    )
    theoretical = _theoretical_from_chart(chart)
    calibration = calibrate_rtp(
        theoretical_rtp=theoretical,
        target_rtp=96.0,
        tolerance=0.5,
    )
    recommendations = generate_calibration_recommendations(
        _game(),
        calibration,
        theoretical,
        calculate_feature_probabilities(_game()),
        decomposition=chart,
    )

    assert calibration.rtp_gap_pp == pytest.approx(0.0, abs=0.01)
    assert any(rec.category == "status" for rec in recommendations)
    assert not any("scatter frequency" in rec.action.lower() for rec in recommendations)


def test_recommendations_include_component_context_and_impact_ordering() -> None:
    chart = RtpDecompositionChart(
        base=5.0,
        free_spins=45.0,
        hold_and_win=0.0,
        jackpot=0.0,
        total_rtp=50.0,
    )
    _, recommendations = _recommendations_for_chart(chart)

    positive_impacts = [
        rec.estimated_rtp_contribution_pp
        for rec in recommendations
        if rec.estimated_rtp_contribution_pp > 0
    ]
    assert positive_impacts == sorted(positive_impacts, reverse=True)

    for rec in recommendations:
        if rec.estimated_rtp_contribution_pp <= 0:
            continue
        assert "expected" in rec.expected_rtp_impact.lower()
        assert "RTP is" in rec.expected_rtp_impact
