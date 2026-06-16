"""Collect per-spin wins for certification analysis (benchmark-only)."""

from __future__ import annotations

from runtime_core.domain.game_version import GameVersion
from runtime_core.runtime.events import EventLogMode
from runtime_core.runtime.executor import SessionExecutor
from runtime_core.runtime.spin_chain import SpinChainRequest
from runtime_core.simulation.models import SimulationProfile


def collect_spin_wins(
    game: GameVersion,
    profile: SimulationProfile,
    *,
    spin_count: int | None = None,
) -> tuple[int, ...]:
    """Execute spin chains in-process and record capped win per chain."""
    total = spin_count if spin_count is not None else profile.spin_count
    executor = SessionExecutor()
    wins: list[int] = []
    for spin_chain_index in range(total):
        request = SpinChainRequest(
            game=game,
            master_seed=profile.master_seed,
            spin_chain_index=spin_chain_index,
            shard_index=0,
            simulation_run_id=profile.simulation_run_id,
            bet_minor_units=profile.bet_minor_units,
            engine_version=profile.resolved_engine_version(),
            event_log_mode=EventLogMode.NONE,
        )
        result = executor.execute_spin_chain(request)
        wins.append(result.total_win_minor_units)
    return tuple(wins)
