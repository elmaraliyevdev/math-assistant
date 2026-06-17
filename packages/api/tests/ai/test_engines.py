"""Explanation and recommendation engine unit tests."""

from __future__ import annotations

import uuid

from app.certification import CERTIFICATION_NOTICE
from app.ai.comparison_engine import explain_comparison, explain_game_version
from app.ai.context_builder import (
    ComparisonArtifactContext,
    GameVersionArtifactContext,
    SimulationArtifactContext,
)
from app.ai.explanation_engine import explain_simulation
from app.ai.recommendation_engine import recommend_calibration
from app.schemas.mathematics import (
    CalibrateResponse,
    CalibrationRecommendationResponse,
    CalibrationResultResponse,
    DiscrepancyAnalysisResponse,
    FeatureProbabilityItem,
    TheoreticalAnalysisResponse,
    TheoreticalRtpResponse,
)
from app.schemas.simulations import (
    ComparisonFeatureFrequencyItem,
    ComparisonMetricItem,
    ComparisonRtpDecompositionItem,
    ConfidenceIntervalSummary,
    ExposureSummary,
    FeatureFrequencyItem,
    HitFrequencySummary,
    RecommendationItem,
    RtpDecompositionChartSummary,
    RtpDecompositionSummary,
    RtpValidationSummary,
    SimulationCompareEntry,
    SimulationCompareResponse,
    SimulationComparisonMetrics,
    SimulationDetailResponse,
    SimulationProgress,
    SimulationResultsResponse,
    SimulationResultsSummary,
    SimulationResultsTotals,
    VolatilityMetricsSummary,
    WinDistributionSummary,
)


def _results(*, rtp: float = 0.51) -> SimulationResultsResponse:
    return SimulationResultsResponse(
        simulation_id=uuid.uuid4(),
        summary=SimulationResultsSummary(
            rtp=rtp,
            uncapped_rtp=rtp,
            volatility=4.0,
            hit_frequency=0.2,
        ),
        totals=SimulationResultsTotals(
            total_bet_minor_units=1000,
            total_win_minor_units=int(1000 * rtp),
        ),
        feature_frequencies=[
            FeatureFrequencyItem(
                feature_name="FREE_SPINS",
                trigger_count=6,
                frequency=0.6,
                one_in_x=1.67,
            ),
        ],
        jackpot_frequencies=[],
        exposure=ExposureSummary(
            truncation_rate=0.01,
            total_truncated_minor_units=10,
            capped_rtp=rtp,
            uncapped_rtp=rtp + 0.01,
            rtp_difference=0.01,
            exposure_cap_applied=True,
        ),
        rtp_decomposition=RtpDecompositionSummary(total_rtp=rtp, categories=[]),
        rtp_validation=RtpValidationSummary(
            target_rtp=96.0,
            actual_rtp=rtp * 100,
            difference=rtp * 100 - 96.0,
            tolerance=0.1,
            within_tolerance=False,
        ),
        rtp_decomposition_chart=RtpDecompositionChartSummary(
            base=5.0,
            free_spins=45.7,
            hold_and_win=0.0,
            jackpot=0.3,
            total_rtp=rtp * 100,
        ),
        confidence_interval=ConfidenceIntervalSummary(
            rtp=rtp,
            lower_bound=rtp - 0.05,
            upper_bound=rtp + 0.05,
            confidence_level=0.95,
        ),
        win_distribution=WinDistributionSummary(
            total_spins=10,
            bet_minor_units_per_spin=100,
            buckets=[],
        ),
        volatility_metrics=VolatilityMetricsSummary(
            mean_win_minor_units=100 * rtp,
            variance=0.0,
            standard_deviation=0.0,
            coefficient_of_variation=None,
        ),
        hit_frequency=HitFrequencySummary(
            hit_frequency=0.2,
            winning_spin_count=2,
            losing_spin_count=8,
        ),
        recommendations=[
            RecommendationItem(
                severity="warning",
                title="RTP Below Target",
                description="Increase paytable values.",
            ),
        ],
        engine_version="runtime-core@1.8.0",
        game_version_content_hash="a" * 64,
        certification_notice=CERTIFICATION_NOTICE,
    )


def test_explain_simulation_grounded_citations(valid_canonical_json: dict) -> None:
    sim_id = uuid.uuid4()
    version_id = uuid.uuid4()
    context = SimulationArtifactContext(
        simulation_id=sim_id,
        game_version_id=version_id,
        spin_count=100,
        bet_minor_units=100,
        results=_results(),
        canonical_json=valid_canonical_json,
        theoretical=TheoreticalAnalysisResponse(
            rtp=TheoreticalRtpResponse(
                totalRtp=0.0512,
                baseRtp=0.0512,
                scatterRtp=0.0,
                lineRtp=0.0512,
                outcomeCount=3125,
                reelSetId="base_game",
            ),
            feature_probabilities=[
                FeatureProbabilityItem(
                    trigger="FREE_SPINS",
                    probability=0.027,
                    one_in_x=37.0,
                ),
            ],
            engine_version="runtime-core@1.8.0",
        ),
    )
    payload = explain_simulation(context)
    assert payload["simulationId"] == str(sim_id)
    assert "FREE_SPINS" in payload["content"]
    assert payload["citations"]
    assert any(
        citation["path"].startswith("mathematics_report")
        for citation in payload["citations"]
    )


def test_recommend_calibration_merges_sources(valid_canonical_json: dict) -> None:
    context = SimulationArtifactContext(
        simulation_id=uuid.uuid4(),
        game_version_id=uuid.uuid4(),
        spin_count=100,
        bet_minor_units=100,
        results=_results(),
        canonical_json=valid_canonical_json,
        calibration=CalibrateResponse(
            theoreticalRtp=TheoreticalRtpResponse(
                totalRtp=0.0512,
                baseRtp=0.0512,
                scatterRtp=0.0,
                lineRtp=0.0512,
                outcomeCount=3125,
                reelSetId="base_game",
            ),
            feature_probabilities=[],
            calibration=CalibrationResultResponse(
                targetRtp=96.0,
                theoreticalRtp=5.12,
                simulatedRtp=51.0,
                targetDelta=-90.88,
                theoryVsSimulationDelta=45.88,
                withinTolerance=False,
                tolerance=0.1,
            ),
            discrepancy=DiscrepancyAnalysisResponse(items=[], summary="gap"),
            recommendations=[
                CalibrationRecommendationResponse(
                    severity="critical",
                    category="paytable",
                    action="Paytable redesign: Re-scale line-pay multipliers across all symbol tiers.",
                    expectedRtpImpact="Estimated +40.90 percentage points toward target RTP.",
                    estimatedRtpContributionPp=40.9,
                    priority=90,
                    discrepancySeverity="critical",
                ),
            ],
            engine_version="runtime-core@1.8.0",
        ),
    )
    payload = recommend_calibration(context, target_rtp=96.0)
    assert payload["recommendations"]
    assert any("Paytable redesign" in rec["action"] for rec in payload["recommendations"])
    assert any(citation["source"] == "calibration_report" for citation in payload["citations"])


def test_explain_comparison_and_game_version(valid_canonical_json: dict) -> None:
    sim_a = uuid.uuid4()
    sim_b = uuid.uuid4()
    detail = SimulationDetailResponse(
        id=sim_a,
        game_version_id=uuid.uuid4(),
        status="completed",
        spin_count=100,
        completed_spin_count=100,
        bet_minor_units=100,
        event_log_mode="none",
        created_at="2026-01-01T00:00:00Z",
        started_at="2026-01-01T00:00:01Z",
        completed_at="2026-01-01T00:00:02Z",
        cancel_requested=False,
        worker_id="worker-1",
        error_message=None,
        progress=SimulationProgress(completed_spins=100, percentage=100),
    )
    comparison = SimulationCompareResponse(
        simulations=[
            SimulationCompareEntry(
                simulation_id=sim_a,
                detail=detail,
                results=_results(rtp=0.51),
                runtime_duration_ms=1000,
            ),
            SimulationCompareEntry(
                simulation_id=sim_b,
                detail=detail.model_copy(update={"id": sim_b}),
                results=_results(rtp=0.62),
                runtime_duration_ms=1200,
            ),
        ],
        comparison=SimulationComparisonMetrics(
            rtp=[
                ComparisonMetricItem(simulation_id=sim_a, value=0.51),
                ComparisonMetricItem(simulation_id=sim_b, value=0.62),
            ],
            volatility=[
                ComparisonMetricItem(simulation_id=sim_a, value=4.0),
                ComparisonMetricItem(simulation_id=sim_b, value=5.0),
            ],
            hit_frequency=[
                ComparisonMetricItem(simulation_id=sim_a, value=0.2),
                ComparisonMetricItem(simulation_id=sim_b, value=0.25),
            ],
            confidence_intervals=[],
            feature_frequency=[
                ComparisonFeatureFrequencyItem(
                    simulation_id=sim_a,
                    feature_name="FREE_SPINS",
                    frequency=0.6,
                ),
                ComparisonFeatureFrequencyItem(
                    simulation_id=sim_b,
                    feature_name="FREE_SPINS",
                    frequency=0.7,
                ),
            ],
            rtp_decomposition=[
                ComparisonRtpDecompositionItem(
                    simulation_id=sim_a,
                    base=5.0,
                    free_spins=45.0,
                    hold_and_win=0.0,
                    jackpot=1.0,
                    total_rtp=51.0,
                ),
            ],
        ),
    )
    compare_payload = explain_comparison(
        ComparisonArtifactContext(comparison=comparison),
    )
    assert len(compare_payload["simulationIds"]) == 2
    assert "RTP" in compare_payload["content"]

    game_payload = explain_game_version(
        GameVersionArtifactContext(
            game_version_id=uuid.uuid4(),
            game_title="Base 5x3",
            canonical_json=valid_canonical_json,
            theoretical=TheoreticalAnalysisResponse(
                rtp=TheoreticalRtpResponse(
                    totalRtp=0.0512,
                    baseRtp=0.0512,
                    scatterRtp=0.0,
                    lineRtp=0.0512,
                    outcomeCount=3125,
                    reelSetId="base_game",
                ),
                feature_probabilities=[
                    FeatureProbabilityItem(
                        trigger="FREE_SPINS",
                        probability=0.027,
                        one_in_x=37.0,
                    ),
                ],
                engine_version="runtime-core@1.8.0",
            ),
        ),
    )
    assert "Base 5x3" in game_payload["content"]
