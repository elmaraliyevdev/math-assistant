"""MathematicsReport assembly."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical.confidence import calculate_rtp_confidence_interval
from runtime_core.mathematical.distribution import calculate_win_distribution
from runtime_core.mathematical.exposure import calculate_exposure_analysis
from runtime_core.mathematical.feature_frequency import calculate_feature_frequencies
from runtime_core.mathematical.hit_frequency import calculate_hit_frequency
from runtime_core.mathematical.insights import enrich_mathematics_report
from runtime_core.mathematical.jackpot_frequency import calculate_jackpot_frequencies
from runtime_core.mathematical.models import MathematicsReport
from runtime_core.mathematical.rtp_decomposition import calculate_rtp_decomposition
from runtime_core.mathematical.rtp import calculate_rtp
from runtime_core.mathematical.volatility import calculate_volatility
from runtime_core.simulation.models import SimulationResult


def build_mathematics_report(
    result: SimulationResult,
    *,
    spin_wins_minor_units: tuple[int, ...] = (),
    game: GameVersion | None = None,
    feature_frequency_tolerance: float = 0.05,
) -> MathematicsReport:
    """
    Build a full mathematical report from simulation aggregates.

    Per-spin metrics require *spin_wins_minor_units* with length equal to
    *result.spin_count*. When *spin_count* is zero, an empty tuple is used.
    """
    spin_wins = _resolve_spin_wins(result, spin_wins_minor_units)
    report = MathematicsReport(
        rtp=calculate_rtp(result),
        hit_frequency=calculate_hit_frequency(result, spin_wins),
        feature_frequencies=calculate_feature_frequencies(result),
        jackpot_frequencies=calculate_jackpot_frequencies(result),
        volatility=calculate_volatility(result, spin_wins),
        exposure=calculate_exposure_analysis(result),
        confidence_interval=calculate_rtp_confidence_interval(result, spin_wins),
        win_distribution=calculate_win_distribution(result, spin_wins),
        rtp_decomposition=calculate_rtp_decomposition(result),
        spin_count=result.spin_count,
        engine_version=result.engine_version,
    )
    if game is not None:
        return enrich_mathematics_report(
            report,
            game=game,
            result=result,
            feature_frequency_tolerance=feature_frequency_tolerance,
        )
    return report


def _resolve_spin_wins(
    result: SimulationResult,
    spin_wins_minor_units: tuple[int, ...],
) -> tuple[int, ...]:
    if result.spin_count == 0:
        return ()
    if not spin_wins_minor_units:
        msg = "spin_wins_minor_units required when spin_count > 0"
        raise ValueError(msg)
    if len(spin_wins_minor_units) != result.spin_count:
        msg = (
            f"spin_wins length {len(spin_wins_minor_units)} "
            f"!= spin_count {result.spin_count}"
        )
        raise ValueError(msg)
    return spin_wins_minor_units
