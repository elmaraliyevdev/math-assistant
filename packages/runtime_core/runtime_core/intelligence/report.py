"""Simulation intelligence report assembly."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.intelligence.clustering_analysis import average_spacing, clustering_score
from runtime_core.intelligence.contribution_analysis import build_contribution_slices
from runtime_core.intelligence.distribution_analysis import build_design_vs_reality
from runtime_core.intelligence.evidence import confidence_from_sample_size, evidence_from_path
from runtime_core.intelligence.feature_analysis import build_feature_dashboards
from runtime_core.intelligence.insights import build_intelligence_recommendations
from runtime_core.intelligence.models import (
    IntelligenceSnapshot,
    MetricExplanation,
    ScatterIntelligence,
    SimulationHeatmap,
    SimulationIntelligenceReport,
)
from runtime_core.intelligence.near_miss_analysis import summarize_near_misses
from runtime_core.intelligence.position_analysis import build_position_highlights, build_reel_reports
from runtime_core.intelligence.symbol_analysis import build_symbol_profiles
from runtime_core.mathematical.models import MathematicsReport
from runtime_core.simulation.models import SimulationResult


def build_simulation_intelligence_report(
    *,
    result: SimulationResult,
    report: MathematicsReport,
    game: GameVersion,
    snapshot: IntelligenceSnapshot | None = None,
) -> SimulationIntelligenceReport:
    intelligence = snapshot or result.intelligence_snapshot
    symbol_profiles = build_symbol_profiles(intelligence, report, game)
    feature_dashboards = build_feature_dashboards(result, report)
    reel_reports = build_reel_reports(intelligence, game)
    contribution_slices = build_contribution_slices(intelligence, report)
    design_vs_reality = build_design_vs_reality(intelligence, result, report, game)
    recommendations = build_intelligence_recommendations(intelligence, result, report)
    unexpected = summarize_near_misses(intelligence)
    why_rtp = _why_rtp_differs(report, intelligence, result)
    scatter = _scatter_intelligence(intelligence, result, symbol_profiles)
    heatmaps = _build_heatmaps(intelligence)
    metric_explanations = _metric_explanations(report, intelligence, result)

    return SimulationIntelligenceReport(
        overview=(
            f"Simulation intelligence for {result.spin_count:,} spins at RTP "
            f"{report.rtp.rtp * 100:.2f}% with {len(recommendations)} evidence-backed insights."
        ),
        why_rtp_differs=why_rtp,
        symbol_profiles=symbol_profiles,
        scatter_intelligence=scatter,
        feature_dashboards=feature_dashboards,
        reel_reports=reel_reports,
        contribution_slices=contribution_slices,
        design_vs_reality=design_vs_reality,
        heatmaps=heatmaps,
        position_highlights=build_position_highlights(intelligence),
        unexpected_findings=unexpected,
        recommendations=recommendations,
        metric_explanations=metric_explanations,
        spin_count=result.spin_count,
        engine_version=result.engine_version,
    )


def _why_rtp_differs(
    report: MathematicsReport,
    snapshot: IntelligenceSnapshot,
    result: SimulationResult,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if report.rtp_validation and not report.rtp_validation.within_tolerance:
        reasons.append(
            f"Observed RTP {report.rtp_validation.actual_rtp * 100:.2f}% differs from target "
            f"{report.rtp_validation.target_rtp * 100:.2f}% by "
            f"{report.rtp_validation.difference * 100:.2f} percentage points.",
        )
    for validation in report.feature_validation:
        if validation.status == "pass":
            continue
        reasons.append(
            f"{validation.feature} triggered at {validation.observed_frequency:.4f} "
            f"vs expected {validation.expected_frequency:.4f}.",
        )
    if snapshot.near_miss_count > 0:
        reasons.append(
            f"Near-miss scatter patterns occurred {snapshot.near_miss_count:,} times, "
            "affecting perceived hit behaviour without completing features.",
        )
    if not reasons:
        reasons.append("Observed RTP aligns with design targets within measured confidence.")
    return tuple(reasons)


def _scatter_intelligence(
    snapshot: IntelligenceSnapshot,
    result: SimulationResult,
    profiles: tuple,
) -> ScatterIntelligence | None:
    scatter_symbols = [
        profile for profile in profiles if "SCATTER" in profile.symbol_id.upper() or profile.symbol_id in {"S", "SC"}
    ]
    if not scatter_symbols and not snapshot.scatter_landings_by_reel:
        return None
    profile = scatter_symbols[0] if scatter_symbols else None
    observed = (
        profile.occurrences / max(snapshot.grid_observation_count, 1) if profile else 0.0
    )
    expected = (
        profile.expected_occurrences / max(snapshot.grid_observation_count, 1) if profile else observed
    )
    symbol_id = profile.symbol_id if profile else "SCATTER"
    spacing = average_spacing(snapshot, symbol_id)
    return ScatterIntelligence(
        observed_frequency=round(observed, 4),
        expected_frequency=round(expected, 4),
        observed_spacing=round(spacing, 2) if spacing is not None else None,
        expected_spacing=None,
        clustering_score=round(clustering_score(snapshot, symbol_id), 4),
        landing_heatmap=dict(snapshot.scatter_landings_by_reel),
        recommendation=None,
    )


def _build_heatmaps(snapshot: IntelligenceSnapshot) -> tuple[SimulationHeatmap, ...]:
    heatmaps: list[SimulationHeatmap] = []
    if snapshot.scatter_landings_by_reel:
        total = max(sum(snapshot.scatter_landings_by_reel.values()), 1)
        heatmaps.append(
            SimulationHeatmap(
                id="scatter-landing",
                label="Scatter landing density",
                mode="entire_simulation",
                cells={
                    key: value / total for key, value in snapshot.scatter_landings_by_reel.items()
                },
            ),
        )
    if snapshot.wild_landings_by_reel:
        total = max(sum(snapshot.wild_landings_by_reel.values()), 1)
        heatmaps.append(
            SimulationHeatmap(
                id="wild-landing",
                label="Wild landing density",
                mode="entire_simulation",
                cells={key: value / total for key, value in snapshot.wild_landings_by_reel.items()},
            ),
        )
    for mode, count in snapshot.feature_mode_grid_counts.items():
        if count > 0:
            heatmaps.append(
                SimulationHeatmap(
                    id=f"mode-{mode.lower()}",
                    label=f"{mode} grid observations",
                    mode=mode,
                    cells={"grids": float(count)},
                ),
            )
    return tuple(heatmaps)


def _metric_explanations(
    report: MathematicsReport,
    snapshot: IntelligenceSnapshot,
    result: SimulationResult,
) -> tuple[MetricExplanation, ...]:
    explanations: list[MetricExplanation] = []
    for feature in report.feature_frequencies:
        one_in = feature.one_in_x
        observed = f"1 in {one_in:.0f}" if one_in else f"{feature.frequency:.4f}"
        explanations.append(
            MetricExplanation(
                metric_id=f"feature-{feature.feature_name}",
                label=f"Observed {feature.feature_name} frequency",
                observed=observed,
                explanation=(
                    f"{feature.feature_name} triggered {feature.trigger_count:,} times across "
                    f"{result.spin_count:,} spins."
                ),
                confidence=confidence_from_sample_size(
                    feature.frequency,
                    feature.frequency,
                    sample_size=result.spin_count,
                ),
                evidence=(
                    evidence_from_path(
                        source="simulation",
                        path=f"featureFrequencies.{feature.feature_name}",
                        value=feature.frequency,
                        spin_count=result.spin_count,
                    ),
                ),
            ),
        )
    if snapshot.scatter_landings_by_reel:
        explanations.append(
            MetricExplanation(
                metric_id="scatter-spacing",
                label="Scatter landing distribution",
                observed=str(snapshot.scatter_landings_by_reel),
                explanation=(
                    "Scatter symbols land unevenly across reels, which can tighten effective spacing "
                    "on reels with fewer landing windows."
                ),
                confidence=confidence_from_sample_size(
                    1.0,
                    1.0,
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
            ),
        )
    return tuple(explanations)
