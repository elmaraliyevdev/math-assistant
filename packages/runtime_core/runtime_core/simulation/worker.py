"""Process-pool shard worker for Monte Carlo simulation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime_core.domain.game_version import GameVersion
from runtime_core.runtime.events import EventLogMode
from runtime_core.runtime.executor import SessionExecutor
from runtime_core.runtime.spin_chain import SpinChainRequest
from runtime_core.simulation.aggregator import PartialAccumulator
from runtime_core.simulation.models import SimulationProfile


@dataclass(frozen=True, slots=True)
class ShardWork:
    game_dict: dict[str, Any]
    profile_dict: dict[str, Any]
    shard_index: int
    spin_start: int
    spin_count: int


def execute_shard(work: ShardWork) -> PartialAccumulator:
    """Run one shard in a worker process with a fresh Runtime Core stack."""
    game = GameVersion.model_validate(work.game_dict)
    profile = SimulationProfile.model_validate(work.profile_dict)
    executor = SessionExecutor()
    accumulator = PartialAccumulator.empty()
    if work.spin_count <= 0:
        return accumulator

    for offset in range(work.spin_count):
        spin_chain_index = work.spin_start + offset
        events_sampled = (
            profile.sample_events > 0 and spin_chain_index < profile.sample_events
        )
        event_mode = profile.event_log_mode if events_sampled else EventLogMode.NONE
        request = SpinChainRequest(
            game=game,
            master_seed=profile.master_seed,
            spin_chain_index=spin_chain_index,
            # Global spin index drives chain RNG; physical shard is work partition only.
            shard_index=0,
            simulation_run_id=profile.simulation_run_id,
            bet_minor_units=profile.bet_minor_units,
            engine_version=profile.resolved_engine_version(),
            event_log_mode=event_mode,
        )
        result = executor.execute_spin_chain(request)
        accumulator = accumulator.add_chain(result, events_sampled=events_sampled)

        if profile.max_faults is not None and profile.max_faults >= 0:
            if accumulator.chain_fault_count > profile.max_faults:
                break

    return accumulator
