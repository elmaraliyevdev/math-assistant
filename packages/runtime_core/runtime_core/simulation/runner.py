"""SimulationRunner — deterministic Monte Carlo orchestration."""

from __future__ import annotations

import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from runtime_core.domain.game_version import GameVersion
from runtime_core.runtime.version import ENGINE_VERSION
from runtime_core.simulation.aggregator import AccumulatorAggregator, PartialAccumulator
from runtime_core.simulation.models import SimulationProfile, SimulationResult
from runtime_core.simulation.sharding import assign_shards
from runtime_core.simulation.worker import ShardWork, execute_shard


class SimulationRunner:
    """Execute N spin chains with deterministic sharding and aggregation."""

    def __init__(self, *, max_workers: int | None = None) -> None:
        self._max_workers = max_workers

    def run(
        self,
        game_version: GameVersion,
        simulation_profile: SimulationProfile,
    ) -> SimulationResult:
        return run_simulation(
            game_version,
            simulation_profile,
            max_workers=self._max_workers,
        )


def run_simulation(
    game_version: GameVersion,
    simulation_profile: SimulationProfile,
    *,
    max_workers: int | None = None,
) -> SimulationResult:
    """Run a Monte Carlo simulation and return aggregated metrics."""
    started = time.perf_counter()
    profile = simulation_profile
    assignments = assign_shards(
        profile.spin_count,
        profile.shard_count,
        master_seed=profile.master_seed,
        simulation_run_id=profile.simulation_run_id,
    )
    game_dict = game_version.to_json_dict()
    profile_dict = profile.model_dump(mode="json", by_alias=True)
    works = [
        ShardWork(
            game_dict=game_dict,
            profile_dict=profile_dict,
            shard_index=assignment.shard_index,
            spin_start=assignment.spin_start,
            spin_count=assignment.spin_count,
        )
        for assignment in assignments
        if assignment.spin_count > 0
    ]

    if not works:
        partials: tuple[PartialAccumulator, ...] = (PartialAccumulator.empty(),)
    elif len(works) == 1:
        partials = (execute_shard(works[0]),)
    else:
        worker_count = max_workers if max_workers is not None else profile.shard_count
        partials = _run_process_pool(works, max_workers=worker_count)

    aggregated = AccumulatorAggregator.aggregate(partials)
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    return _to_result(
        aggregated,
        spin_count=profile.spin_count,
        shard_count=profile.shard_count,
        elapsed_time_ms=elapsed_ms,
        engine_version=profile.resolved_engine_version(),
    )


def _run_process_pool(
    works: list[ShardWork],
    *,
    max_workers: int,
) -> tuple[PartialAccumulator, ...]:
    results: list[PartialAccumulator] = []
    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        future_map = {pool.submit(execute_shard, work): work for work in works}
        for future in as_completed(future_map):
            results.append(future.result())
    return tuple(results)


def _to_result(
    aggregated: PartialAccumulator,
    *,
    spin_count: int,
    shard_count: int,
    elapsed_time_ms: int,
    engine_version: str,
) -> SimulationResult:
    return SimulationResult(
        spin_count=spin_count,
        shard_count=shard_count,
        elapsed_time_ms=elapsed_time_ms,
        total_bet_minor_units=aggregated.total_bet_minor_units,
        total_win_minor_units=aggregated.total_win_minor_units,
        uncapped_win_minor_units=aggregated.uncapped_win_minor_units,
        exposure_truncation_count=aggregated.exposure_truncation_count,
        exposure_truncated_minor_units=aggregated.exposure_truncated_minor_units,
        chain_fault_count=aggregated.chain_fault_count,
        limit_hit_count=aggregated.limit_hit_count,
        feature_trigger_counts=dict(aggregated.feature_trigger_counts),
        jackpot_counts=dict(aggregated.jackpot_counts),
        win_by_rtp_category_minor_units=dict(aggregated.win_by_rtp_category_minor_units),
        nested_feature_entries=aggregated.nested_feature_entries,
        event_sample_count=aggregated.event_sample_count,
        engine_version=engine_version or ENGINE_VERSION,
    )
