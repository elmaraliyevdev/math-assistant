"""Evidence-backed intelligence recommendations."""

from __future__ import annotations

from runtime_core.intelligence.evidence import confidence_from_sample_size, evidence_from_path
from runtime_core.intelligence.models import IntelligenceRecommendation, IntelligenceSnapshot
from runtime_core.mathematical.models import MathematicsReport, RecommendationResult
from runtime_core.simulation.models import SimulationResult


def build_intelligence_recommendations(
    snapshot: IntelligenceSnapshot,
    result: SimulationResult,
    report: MathematicsReport,
) -> tuple[IntelligenceRecommendation, ...]:
    recommendations: list[IntelligenceRecommendation] = []

    for item in report.recommendations:
        recommendations.append(
            _from_mathematics_recommendation(item, result.spin_count),
        )

    for validation in report.feature_validation:
        if validation.status == "pass":
            continue
        recommendations.append(
            IntelligenceRecommendation(
                id=f"feature-{validation.feature}",
                title=f"{validation.feature} frequency mismatch",
                reason=validation.feature,
                recommendation=(
                    f"Adjust {validation.feature} trigger conditions — observed "
                    f"{validation.observed_frequency:.4f} vs expected {validation.expected_frequency:.4f}."
                ),
                confidence=confidence_from_sample_size(
                    validation.observed_frequency,
                    validation.expected_frequency,
                    sample_size=result.spin_count,
                ),
                evidence=(
                    evidence_from_path(
                        source="simulation",
                        path=f"featureValidation.{validation.feature}",
                        value=validation.observed_frequency,
                        spin_count=result.spin_count,
                    ),
                ),
                expected_improvement="Align feature frequency with design intent",
            ),
        )

    if snapshot.scatter_landings_by_reel:
        reel_key = min(
            snapshot.scatter_landings_by_reel,
            key=lambda key: snapshot.scatter_landings_by_reel[key],
        )
        recommendations.append(
            IntelligenceRecommendation(
                id="scatter-spacing",
                title="Increase scatter spacing",
                reason="Uneven scatter landings across reels",
                recommendation=f"Increase valid scatter landing windows on Reel {int(reel_key) + 1}.",
                confidence=confidence_from_sample_size(
                    snapshot.scatter_landings_by_reel[reel_key],
                    sum(snapshot.scatter_landings_by_reel.values())
                    / max(len(snapshot.scatter_landings_by_reel), 1),
                    sample_size=snapshot.grid_observation_count,
                ),
                evidence=(
                    evidence_from_path(
                        source="simulation",
                        path="intelligenceSnapshot.scatterLandingsByReel",
                        value=snapshot.scatter_landings_by_reel,
                        spin_count=result.spin_count,
                    ),
                ),
                affected_reels=(int(reel_key),),
                affected_symbols=("SCATTER",),
                expected_improvement="Better spacing and feature entry balance",
            ),
        )

    return tuple(recommendations)


def _from_mathematics_recommendation(
    item: RecommendationResult,
    spin_count: int,
) -> IntelligenceRecommendation:
    return IntelligenceRecommendation(
        id=f"math-{item.title.lower().replace(' ', '-')}",
        title=item.title,
        reason=item.description,
        recommendation=item.description,
        confidence=confidence_from_sample_size(1.0, 1.0, sample_size=spin_count),
        evidence=(
            evidence_from_path(
                source="mathematics_report",
                path=f"recommendations.{item.title}",
                value=item.severity,
                spin_count=spin_count,
            ),
        ),
        expected_improvement="Improve mathematical alignment",
    )
