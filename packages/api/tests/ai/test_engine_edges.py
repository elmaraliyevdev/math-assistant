"""Additional engine edge-case coverage."""

from __future__ import annotations

import uuid

from app.ai.comparison_engine import explain_comparison
from app.ai.context_builder import ComparisonArtifactContext, feature_frequency_map
from app.ai.grounding import cite
from app.ai.recommendation_engine import recommend_calibration
from app.ai.context_builder import SimulationArtifactContext
from tests.ai.test_engines import _results


def test_recommend_without_target_or_calibration(valid_canonical_json: dict) -> None:
    results = _results()
    results = results.model_copy(
        update={
            "rtp_validation": None,
            "recommendations": [],
        },
    )
    context = SimulationArtifactContext(
        simulation_id=uuid.uuid4(),
        game_version_id=uuid.uuid4(),
        spin_count=10,
        bet_minor_units=100,
        results=results,
        canonical_json=valid_canonical_json,
    )
    payload = recommend_calibration(context, target_rtp=None)
    assert payload["recommendations"]
    assert payload["recommendations"][0]["category"] == "status"


def test_compare_single_simulation_rtp_branch(valid_canonical_json: dict) -> None:
    from app.schemas.simulations import (
        ComparisonMetricItem,
        SimulationCompareEntry,
        SimulationCompareResponse,
        SimulationComparisonMetrics,
        SimulationDetailResponse,
        SimulationProgress,
    )

    sim_id = uuid.uuid4()
    detail = SimulationDetailResponse(
        id=sim_id,
        game_version_id=uuid.uuid4(),
        status="completed",
        spin_count=10,
        completed_spin_count=10,
        bet_minor_units=100,
        event_log_mode="none",
        created_at="2026-01-01T00:00:00Z",
        started_at=None,
        completed_at=None,
        cancel_requested=False,
        worker_id=None,
        error_message=None,
        progress=SimulationProgress(completed_spins=10, percentage=100),
    )
    comparison = SimulationCompareResponse(
        simulations=[
            SimulationCompareEntry(
                simulation_id=sim_id,
                detail=detail,
                results=_results(),
                runtime_duration_ms=None,
            ),
        ],
        comparison=SimulationComparisonMetrics(
            rtp=[ComparisonMetricItem(simulation_id=sim_id, value=0.51)],
            volatility=[],
            hit_frequency=[],
            confidence_intervals=[],
            feature_frequency=[],
            rtp_decomposition=[],
        ),
    )
    payload = explain_comparison(ComparisonArtifactContext(comparison=comparison))
    assert "Insufficient simulations" in payload["content"]


def test_feature_frequency_map_helper() -> None:
    results = _results()
    mapping = feature_frequency_map(results)
    assert mapping["FREE_SPINS"] == 0.6


def test_citation_without_value() -> None:
    citation = cite(label="Report", source="simulation_results", path="rtp")
    assert citation.inline() == "(simulation_results.rtp)"
