"""Async simulation orchestration with per-shard process pool execution."""

from __future__ import annotations

import asyncio
import time
import uuid
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor

from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical import MathematicsReport, build_mathematics_report
from runtime_core.mathematical.exposure import calculate_exposure_analysis
from runtime_core.mathematical.feature_frequency import calculate_feature_frequencies
from runtime_core.mathematical.jackpot_frequency import calculate_jackpot_frequencies
from runtime_core.mathematical.insights import enrich_mathematics_report
from runtime_core.mathematical.models import (
    ConfidenceIntervalResult,
    HitFrequencyResult,
    VolatilityResult,
    WinDistributionResult,
)
from runtime_core.mathematical.rtp import calculate_rtp
from runtime_core.mathematical.rtp_decomposition import calculate_rtp_decomposition
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

from app.adapters.simulation_types import SimulationExecutionOutcome
from app.exceptions.simulation import SimulationJobCancelledError
from app.jobs.simulation_logging import log_simulation_event

ProgressCallback = Callable[[int, int], None]
ShardLifecycleCallback = Callable[[int, int, int], None]


async def execute_simulation_async(
    game: GameVersion,
    profile: SimulationProfile,
    *,
    simulation_id: uuid.UUID,
    process_pool: ProcessPoolExecutor,
    on_progress: ProgressCallback | None = None,
    on_shard_started: ShardLifecycleCallback | None = None,
    on_shard_completed: ShardLifecycleCallback | None = None,
    should_cancel: Callable[[], bool] | None = None,
    spin_wins_detail_limit: int = 10_000,
) -> SimulationExecutionOutcome:
    """Run simulation shards in the shared process pool with progress updates."""
    if should_cancel and should_cancel():
        raise SimulationJobCancelledError

    started = time.perf_counter()
    loop = asyncio.get_running_loop()
    engine_result = await _run_sharded_simulation(
        loop,
        process_pool,
        game,
        profile,
        simulation_id=simulation_id,
        on_progress=on_progress,
        on_shard_started=on_shard_started,
        on_shard_completed=on_shard_completed,
        should_cancel=should_cancel,
    )

    if should_cancel and should_cancel():
        raise SimulationJobCancelledError

    if profile.spin_count <= spin_wins_detail_limit:
        spin_wins = await _collect_spin_wins_async(
            loop,
            process_pool,
            game,
            profile,
            on_progress=on_progress,
            should_cancel=should_cancel,
        )
        mathematics_report = _build_detailed_mathematics_report(
            engine_result,
            spin_wins,
            game=game,
        )
    else:
        mathematics_report = _build_aggregate_mathematics_report(engine_result, game=game)

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    log_simulation_event(
        "simulation_execution_finished",
        simulation_id=str(simulation_id),
        spin_count=profile.spin_count,
        shard_count=profile.shard_count,
        elapsed_ms=elapsed_ms,
    )

    return SimulationExecutionOutcome(
        engine_result=engine_result,
        mathematics_report=mathematics_report,
    )


async def _run_sharded_simulation(
    loop: asyncio.AbstractEventLoop,
    process_pool: ProcessPoolExecutor,
    game: GameVersion,
    profile: SimulationProfile,
    *,
    simulation_id: uuid.UUID,
    on_progress: ProgressCallback | None,
    on_shard_started: ShardLifecycleCallback | None,
    on_shard_completed: ShardLifecycleCallback | None,
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

    partials: list = []
    completed_spins = 0
    total_shards = len(works)

    for work in works:
        if should_cancel and should_cancel():
            raise SimulationJobCancelledError

        if on_shard_started:
            on_shard_started(work.shard_index, total_shards, profile.spin_count)

        log_simulation_event(
            "simulation_shard_started",
            simulation_id=str(simulation_id),
            shard_index=work.shard_index,
            shard_spin_count=work.spin_count,
            total_shards=total_shards,
        )

        partial = await loop.run_in_executor(process_pool, execute_shard, work)
        partials.append(partial)
        completed_spins += work.spin_count

        if on_shard_completed:
            on_shard_completed(work.shard_index, completed_spins, profile.spin_count)
        if on_progress:
            on_progress(completed_spins, profile.spin_count)

        log_simulation_event(
            "simulation_shard_completed",
            simulation_id=str(simulation_id),
            shard_index=work.shard_index,
            completed_spins=completed_spins,
            total_spins=profile.spin_count,
            percentage=round((completed_spins / profile.spin_count) * 100, 2)
            if profile.spin_count
            else 100.0,
        )

    aggregated = AccumulatorAggregator.aggregate(tuple(partials))
    return _to_engine_result(aggregated, profile=profile, elapsed_time_ms=0)


async def _collect_spin_wins_async(
    loop: asyncio.AbstractEventLoop,
    process_pool: ProcessPoolExecutor,
    game: GameVersion,
    profile: SimulationProfile,
    *,
    on_progress: ProgressCallback | None,
    should_cancel: Callable[[], bool] | None,
) -> tuple[int, ...]:
    if profile.spin_count <= 0:
        return ()

    return await loop.run_in_executor(
        process_pool,
        _collect_spin_wins_sync,
        game,
        profile,
    )


def _collect_spin_wins_sync(
    game: GameVersion,
    profile: SimulationProfile,
) -> tuple[int, ...]:
    executor = SessionExecutor()
    wins: list[int] = []
    for spin_chain_index in range(profile.spin_count):
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


def _build_detailed_mathematics_report(
    result: SimulationResult,
    spin_wins: tuple[int, ...],
    *,
    game: GameVersion,
) -> MathematicsReport:
    return build_mathematics_report(result, spin_wins_minor_units=spin_wins, game=game)


def _build_aggregate_mathematics_report(
    result: SimulationResult,
    *,
    game: GameVersion,
) -> MathematicsReport:
    rtp = calculate_rtp(result)
    mean_win = rtp.total_win_minor_units / result.spin_count if result.spin_count else 0.0
    base = MathematicsReport(
        rtp=rtp,
        hit_frequency=HitFrequencyResult(
            hit_frequency=0.0,
            winning_spin_count=0,
            losing_spin_count=result.spin_count,
        ),
        feature_frequencies=calculate_feature_frequencies(result),
        jackpot_frequencies=calculate_jackpot_frequencies(result),
        volatility=VolatilityResult(
            mean_win_minor_units=mean_win,
            variance=0.0,
            standard_deviation=0.0,
            coefficient_of_variation=None,
        ),
        exposure=calculate_exposure_analysis(result),
        confidence_interval=ConfidenceIntervalResult(
            lower_bound=rtp.rtp,
            upper_bound=rtp.rtp,
            confidence_level=0.95,
        ),
        win_distribution=WinDistributionResult(
            total_spins=result.spin_count,
            bet_minor_units_per_spin=(
                result.total_bet_minor_units // result.spin_count
                if result.spin_count
                else 0
            ),
            buckets=(),
        ),
        rtp_decomposition=calculate_rtp_decomposition(result),
        spin_count=result.spin_count,
        engine_version=result.engine_version,
    )
    return enrich_mathematics_report(base, game=game, result=result)


def _to_engine_result(
    aggregated,
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
        engineVersion=engine_version,
    )


__all__ = [
    "execute_simulation_async",
]
