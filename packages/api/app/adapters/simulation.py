"""Simulation execution adapter — public runtime_core APIs only."""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable

from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical import MathematicsReport, build_mathematics_report
from runtime_core.runtime.events import EventLogMode
from runtime_core.runtime.executor import SessionExecutor
from runtime_core.runtime.spin_chain import SpinChainRequest
from runtime_core.runtime.version import ENGINE_VERSION
from runtime_core.simulation import (
    AccumulatorAggregator,
    PartialAccumulator,
    SimulationProfile,
    SimulationResult,
    assign_shards,
)
from runtime_core.simulation.worker import ShardWork, execute_shard

from app.adapters.simulation_sharding import compute_shard_count
from app.adapters.simulation_types import SimulationExecutionOutcome
from app.exceptions.simulation import SimulationJobCancelledError


def build_simulation_profile(
    *,
    simulation_id: uuid.UUID,
    spin_count: int,
    bet_minor_units: int,
    event_log_mode: EventLogMode,
    master_seed: str | None,
    engine_version: str,
    shard_count: int | None = None,
) -> SimulationProfile:
    resolved_shard_count = shard_count or compute_shard_count(spin_count)
    return SimulationProfile(
        spinCount=spin_count,
        shardCount=resolved_shard_count,
        masterSeed=master_seed or f"sim-{simulation_id}",
        simulationRunId=str(simulation_id),
        eventLogMode=event_log_mode,
        betMinorUnits=bet_minor_units,
        engineVersion=engine_version,
    )


def execute_simulation_with_report(
    game: GameVersion,
    profile: SimulationProfile,
    *,
    on_progress: Callable[[int, int], None] | None = None,
    should_cancel: Callable[[], bool] | None = None,
    spin_wins_detail_limit: int = 10_000,
) -> SimulationExecutionOutcome:
    """Synchronous simulation path used in unit tests and tooling."""
    if should_cancel and should_cancel():
        raise SimulationJobCancelledError

    started = time.perf_counter()
    engine_result = _run_sharded_simulation_sync(
        game,
        profile,
        on_progress=on_progress,
        should_cancel=should_cancel,
    )

    if should_cancel and should_cancel():
        raise SimulationJobCancelledError

    if profile.spin_count <= spin_wins_detail_limit:
        spin_wins = _collect_spin_wins_sync(game, profile, should_cancel=should_cancel)
        mathematics_report = build_mathematics_report(
            engine_result,
            spin_wins_minor_units=spin_wins,
            game=game,
        )
    else:
        from app.adapters.simulation_runner import _build_aggregate_mathematics_report

        mathematics_report = _build_aggregate_mathematics_report(engine_result, game=game)

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    engine_result = engine_result.model_copy(update={"elapsedTimeMs": elapsed_ms})
    return SimulationExecutionOutcome(
        engine_result=engine_result,
        mathematics_report=mathematics_report,
    )


def _run_sharded_simulation_sync(
    game: GameVersion,
    profile: SimulationProfile,
    *,
    on_progress: Callable[[int, int], None] | None,
    should_cancel: Callable[[], bool] | None,
) -> SimulationResult:
    assignments = assign_shards(
        profile.spin_count,
        profile.shard_count,
        master_seed=profile.master_seed,
        simulation_run_id=profile.simulation_run_id,
    )
    game_dict = game.to_json_dict()
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
        aggregated = AccumulatorAggregator.aggregate((PartialAccumulator.empty(),))
        return _to_engine_result(aggregated, profile=profile, elapsed_time_ms=0)

    partials: list[PartialAccumulator] = []
    completed_spins = 0
    for work in works:
        if should_cancel and should_cancel():
            raise SimulationJobCancelledError
        partials.append(execute_shard(work))
        completed_spins += work.spin_count
        if on_progress:
            on_progress(completed_spins, profile.spin_count)

    aggregated = AccumulatorAggregator.aggregate(tuple(partials))
    return _to_engine_result(aggregated, profile=profile, elapsed_time_ms=0)


def _collect_spin_wins_sync(
    game: GameVersion,
    profile: SimulationProfile,
    *,
    should_cancel: Callable[[], bool] | None = None,
) -> tuple[int, ...]:
    if profile.spin_count <= 0:
        return ()
    executor = SessionExecutor()
    wins: list[int] = []
    for spin_chain_index in range(profile.spin_count):
        if should_cancel and should_cancel():
            raise SimulationJobCancelledError
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


def _to_engine_result(
    aggregated: PartialAccumulator,
    *,
    profile: SimulationProfile,
    elapsed_time_ms: int,
) -> SimulationResult:
    engine_version = profile.resolved_engine_version() or ENGINE_VERSION
    return SimulationResult(
        spinCount=profile.spin_count,
        shardCount=profile.shard_count,
        elapsedTimeMs=elapsed_time_ms,
        totalBetMinorUnits=aggregated.total_bet_minor_units,
        totalWinMinorUnits=aggregated.total_win_minor_units,
        uncappedWinMinorUnits=aggregated.uncapped_win_minor_units,
        exposureTruncationCount=aggregated.exposure_truncation_count,
        exposureTruncatedMinorUnits=aggregated.exposure_truncated_minor_units,
        chainFaultCount=aggregated.chain_fault_count,
        limitHitCount=aggregated.limit_hit_count,
        featureTriggerCounts=dict(aggregated.feature_trigger_counts),
        jackpotCounts=dict(aggregated.jackpot_counts),
        winByRtpCategoryMinorUnits=dict(aggregated.win_by_rtp_category_minor_units),
        nestedFeatureEntries=aggregated.nested_feature_entries,
        eventSampleCount=aggregated.event_sample_count,
        intelligenceSnapshot=aggregated.intelligence_snapshot.model_dump(mode="json", by_alias=True),
        engineVersion=engine_version,
    )
