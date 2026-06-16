"""Execute a single simulation shard (runtime_core)."""

from __future__ import annotations

import uuid

from runtime_core.domain.game_version import GameVersion
from runtime_core.runtime.events import EventLogMode
from runtime_core.simulation import PartialAccumulator, assign_shards
from runtime_core.simulation.worker import ShardWork, execute_shard

from app.adapters.simulation import build_simulation_profile


def execute_simulation_shard(
    *,
    simulation_id: uuid.UUID,
    game_canonical_json: dict,
    spin_count: int,
    bet_minor_units: int,
    event_log_mode: str,
    master_seed: str | None,
    engine_version: str | None,
    shard_index: int,
    total_shard_count: int,
) -> PartialAccumulator:
    """Run one shard synchronously using runtime_core execute_shard."""
    event_mode = EventLogMode(event_log_mode)
    profile = build_simulation_profile(
        simulation_id=simulation_id,
        spin_count=spin_count,
        bet_minor_units=bet_minor_units,
        event_log_mode=event_mode,
        master_seed=master_seed,
        engine_version=engine_version,
        shard_count=total_shard_count,
    )
    assignments = assign_shards(
        profile.spin_count,
        profile.shard_count,
        master_seed=profile.master_seed,
        simulation_run_id=profile.simulation_run_id,
    )
    assignment = next(
        (item for item in assignments if item.shard_index == shard_index),
        None,
    )
    if assignment is None or assignment.spin_count <= 0:
        return PartialAccumulator.empty()

    game = GameVersion.model_validate(game_canonical_json)
    work = ShardWork(
        game_dict=game.to_json_dict(),
        profile_dict=profile.model_dump(mode="json", by_alias=True),
        shard_index=assignment.shard_index,
        spin_start=assignment.spin_start,
        spin_count=assignment.spin_count,
    )
    return execute_shard(work)
