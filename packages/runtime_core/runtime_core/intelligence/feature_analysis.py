"""Feature intelligence dashboards."""

from __future__ import annotations

from runtime_core.intelligence.evidence import confidence_from_sample_size
from runtime_core.intelligence.models import FeatureIntelligenceDashboard
from runtime_core.mathematical.models import FeatureFrequencyResult, MathematicsReport
from runtime_core.simulation.models import SimulationResult


def build_feature_dashboards(
    result: SimulationResult,
    report: MathematicsReport,
) -> tuple[FeatureIntelligenceDashboard, ...]:
    total_bet = max(report.rtp.total_bet_minor_units, 1)
    validation_by_feature = {
        item.feature: item for item in report.feature_validation
    }
    dashboards: list[FeatureIntelligenceDashboard] = []
    for feature in report.feature_frequencies:
        validation = validation_by_feature.get(feature.feature_name)
        expected = validation.expected_frequency if validation else None
        category_win = result.win_by_rtp_category_minor_units.get(feature.feature_name, 0)
        if category_win == 0 and feature.feature_name == "FREE_SPINS":
            category_win = result.win_by_rtp_category_minor_units.get("FREE_SPINS", 0)
        rtp_share = (category_win / total_bet) * 100.0
        confidence = confidence_from_sample_size(
            feature.frequency,
            expected if expected is not None else feature.frequency,
            sample_size=result.spin_count,
        )
        health = "Healthy"
        if validation and validation.status != "pass":
            health = "Warning"
        dashboards.append(
            FeatureIntelligenceDashboard(
                feature_name=feature.feature_name,
                observed_frequency=feature.frequency,
                expected_frequency=expected,
                average_entry_win_minor_units=0.0,
                average_duration=None,
                average_retriggers=(
                    result.nested_feature_entries / max(feature.trigger_count, 1)
                    if feature.trigger_count > 0
                    else None
                ),
                rtp_contribution_percent=round(rtp_share, 2),
                variance=report.volatility.variance,
                confidence=confidence,
                health=health,
            ),
        )
    return tuple(dashboards)
