"""Golden mathematical test helpers."""

from __future__ import annotations

from runtime_core.simulation.models import SimulationResult


def sample_simulation_result(
    *,
    spin_count: int = 4,
    total_bet: int = 4000,
    total_win: int = 7500,
    uncapped_win: int = 8000,
    exposure_truncations: int = 1,
    exposure_truncated: int = 500,
    feature_triggers: dict[str, int] | None = None,
    jackpot_counts: dict[str, int] | None = None,
) -> SimulationResult:
    return SimulationResult(
        spin_count=spin_count,
        shard_count=1,
        elapsed_time_ms=10,
        total_bet_minor_units=total_bet,
        total_win_minor_units=total_win,
        uncapped_win_minor_units=uncapped_win,
        exposure_truncation_count=exposure_truncations,
        exposure_truncated_minor_units=exposure_truncated,
        chain_fault_count=0,
        limit_hit_count=0,
        feature_trigger_counts=feature_triggers or {"FREE_SPINS": 1},
        jackpot_counts=jackpot_counts or {"MINI": 1},
        event_sample_count=0,
        engine_version="runtime-core@1.8.0",
    )


SAMPLE_SPIN_WINS: tuple[int, ...] = (0, 500, 2000, 5000)
