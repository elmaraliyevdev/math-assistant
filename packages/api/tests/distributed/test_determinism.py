"""Shard count determinism tests."""

from __future__ import annotations

import uuid

from runtime_core.domain.game_version import GameVersion
from runtime_core.runtime.events import EventLogMode
from runtime_core.runtime.version import ENGINE_VERSION
from runtime_core.simulation import assign_shards
from runtime_core.simulation.worker import ShardWork, execute_shard

from app.adapters.simulation import build_simulation_profile
from app.distributed.aggregation_service import merge_partials


def _run_with_shard_count(
    game: GameVersion,
    simulation_id: uuid.UUID,
    spin_count: int,
    shard_count: int,
) -> dict:
    profile = build_simulation_profile(
        simulation_id=simulation_id,
        spin_count=spin_count,
        bet_minor_units=100,
        event_log_mode=EventLogMode.NONE,
        master_seed="determinism-seed",
        engine_version=ENGINE_VERSION,
        shard_count=shard_count,
    )
    assignments = assign_shards(
        profile.spin_count,
        profile.shard_count,
        master_seed=profile.master_seed,
        simulation_run_id=profile.simulation_run_id,
    )
    game_dict = game.to_json_dict()
    profile_dict = profile.model_dump(mode="json", by_alias=True)
    partials = []
    for assignment in assignments:
        if assignment.spin_count <= 0:
            continue
        work = ShardWork(
            game_dict=game_dict,
            profile_dict=profile_dict,
            shard_index=assignment.shard_index,
            spin_start=assignment.spin_start,
            spin_count=assignment.spin_count,
        )
        partials.append(execute_shard(work))
    merged = merge_partials(partials)
    return {
        "total_bet": merged.total_bet_minor_units,
        "total_win": merged.total_win_minor_units,
        "spin_count": merged.spin_count,
    }


def test_shard_count_invariance(valid_canonical_json: dict) -> None:
    game = GameVersion.model_validate(valid_canonical_json)
    simulation_id = uuid.uuid4()
    spin_count = 40
    results = [
        _run_with_shard_count(game, simulation_id, spin_count, shard_count)
        for shard_count in (1, 2, 4, 8, 16)
    ]
    baseline = results[0]
    for result in results[1:]:
        assert result == baseline
