"""Design intent vs observed simulation behaviour."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.intelligence.evidence import confidence_from_sample_size
from runtime_core.intelligence.models import DesignVsRealityItem, IntelligenceSnapshot
from runtime_core.mathematical.models import MathematicsReport
from runtime_core.simulation.models import SimulationResult


def _status_from_gap(gap: float, warn: float, error: float) -> str:
    if gap <= warn:
        return "green"
    if gap <= error:
        return "yellow"
    return "red"


def build_design_vs_reality(
    snapshot: IntelligenceSnapshot,
    result: SimulationResult,
    report: MathematicsReport,
    game: GameVersion,
) -> tuple[DesignVsRealityItem, ...]:
    items: list[DesignVsRealityItem] = []
    metadata = game.metadata
    if metadata.volatility_target:
        observed = report.volatility.coefficient_of_variation or report.volatility.standard_deviation
        confidence = confidence_from_sample_size(
            observed,
            observed,
            sample_size=result.spin_count,
        )
        items.append(
            DesignVsRealityItem(
                metric_id="volatility",
                label="Volatility",
                target=metadata.volatility_target,
                observed=f"{observed:.2f}",
                status="green",
                confidence=confidence,
            ),
        )

    if metadata.rtp_target is not None:
        target = metadata.rtp_target.percent / 100.0
        actual = report.rtp.rtp
        gap = abs(actual - target)
        tolerance = metadata.rtp_target.tolerance or 0.01
        items.append(
            DesignVsRealityItem(
                metric_id="rtp-target",
                label="RTP target",
                target=f"{target * 100:.2f}%",
                observed=f"{actual * 100:.2f}%",
                status=_status_from_gap(gap, tolerance, tolerance * 2),
                confidence=confidence_from_sample_size(actual, target, sample_size=result.spin_count),
            ),
        )

    for validation in report.feature_validation:
        gap = abs(validation.difference)
        items.append(
            DesignVsRealityItem(
                metric_id=f"feature-{validation.feature}",
                label=f"{validation.feature} frequency",
                target=f"{validation.expected_frequency:.4f}",
                observed=f"{validation.observed_frequency:.4f}",
                status=_status_from_gap(gap, 0.02, 0.05),
                confidence=confidence_from_sample_size(
                    validation.observed_frequency,
                    validation.expected_frequency,
                    sample_size=result.spin_count,
                ),
            ),
        )

    wild_observed = sum(snapshot.wild_landings_by_reel.values())
    scatter_observed = sum(snapshot.scatter_landings_by_reel.values())
    if snapshot.grid_observation_count > 0:
        wild_rate = wild_observed / snapshot.grid_observation_count
        scatter_rate = scatter_observed / snapshot.grid_observation_count
        items.append(
            DesignVsRealityItem(
                metric_id="wild-frequency",
                label="Wild landing rate",
                target="design reel composition",
                observed=f"{wild_rate:.4f}",
                status="green" if wild_rate > 0 else "yellow",
                confidence=confidence_from_sample_size(
                    wild_rate,
                    wild_rate,
                    sample_size=snapshot.grid_observation_count,
                ),
            ),
        )
        items.append(
            DesignVsRealityItem(
                metric_id="scatter-frequency",
                label="Scatter landing rate",
                target="design reel composition",
                observed=f"{scatter_rate:.4f}",
                status="green" if scatter_rate > 0 else "yellow",
                confidence=confidence_from_sample_size(
                    scatter_rate,
                    scatter_rate,
                    sample_size=snapshot.grid_observation_count,
                ),
            ),
        )

    return tuple(items)
