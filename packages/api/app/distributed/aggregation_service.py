"""Merge shard partial accumulators and persist simulation results."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical import MathematicsReport
from runtime_core.mathematical.exposure import calculate_exposure_analysis
from runtime_core.runtime.events import EventLogMode
from runtime_core.mathematical.feature_frequency import calculate_feature_frequencies
from runtime_core.mathematical.insights import enrich_mathematics_report
from runtime_core.mathematical.jackpot_frequency import calculate_jackpot_frequencies
from runtime_core.mathematical.models import (
    ConfidenceIntervalResult,
    HitFrequencyResult,
    VolatilityResult,
    WinDistributionResult,
)
from runtime_core.mathematical.rtp import calculate_rtp
from runtime_core.mathematical.rtp_decomposition import calculate_rtp_decomposition
from runtime_core.runtime.version import ENGINE_VERSION
from runtime_core.simulation import AccumulatorAggregator, PartialAccumulator, SimulationResult
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters.simulation import build_simulation_profile
from app.config import Settings
from app.db.models.simulation import Simulation, SimulationStatus
from app.db.models.simulation_result import SimulationResult as SimulationResultRow
from app.db.models.simulation_shard import SimulationShardStatus
from app.db.repositories.game_version_repository import GameVersionRepository
from app.db.repositories.simulation_repository import SimulationRepository
from app.db.repositories.simulation_result_repository import SimulationResultRepository
from app.db.repositories.simulation_shard_repository import SimulationShardRepository
from app.distributed.accumulator_codec import partial_accumulator_from_dict
from app.jobs.simulation_logging import log_simulation_event
from app.services.platform_events import notify_simulation_finished_by_id


@dataclass(frozen=True, slots=True)
class AggregationService:
    session_factory: async_sessionmaker[AsyncSession]
    settings: Settings

    async def try_finalize(self, simulation_id: uuid.UUID) -> bool:
        async with self.session_factory() as session:
            simulations = SimulationRepository(session)
            shards_repo = SimulationShardRepository(session)
            simulation = await simulations.get_by_id(simulation_id)
            if simulation is None or simulation.status in {
                SimulationStatus.COMPLETED,
                SimulationStatus.FAILED,
            }:
                return False

            shards = await shards_repo.list_by_simulation_id(simulation_id)
            if not shards:
                return False

            terminal = {
                SimulationShardStatus.COMPLETED,
                SimulationShardStatus.FAILED,
                SimulationShardStatus.CANCELLED,
            }
            if any(shard.status not in terminal for shard in shards):
                return False

            if simulation.cancel_requested:
                await self._mark_cancelled(simulations, simulation)
                await session.commit()
                return True

            failed = [s for s in shards if s.status == SimulationShardStatus.FAILED]
            if failed:
                simulation.status = SimulationStatus.FAILED
                simulation.error_message = failed[0].error_message or "Shard execution failed"
                simulation.completed_at = datetime.now(tz=UTC)
                await session.commit()
                await notify_simulation_finished_by_id(self.session_factory, simulation_id)
                return True

            partials = [
                partial_accumulator_from_dict(shard.partial_result or {})
                for shard in shards
                if shard.status == SimulationShardStatus.COMPLETED
            ]
            if not partials:
                return False

            aggregated = AccumulatorAggregator.aggregate(tuple(partials))
            game_versions = GameVersionRepository(session)
            game_version = await game_versions.get_by_id(simulation.game_version_id)
            if game_version is None:
                simulation.status = SimulationStatus.FAILED
                simulation.error_message = "game version not found"
                simulation.completed_at = datetime.now(tz=UTC)
                await session.commit()
                return True

            profile = build_simulation_profile(
                simulation_id=simulation.id,
                spin_count=simulation.spin_count,
                bet_minor_units=simulation.bet_minor_units,
                event_log_mode=EventLogMode(simulation.event_log_mode),
                master_seed=simulation.master_seed,
                engine_version=game_version.engine_version,
                shard_count=simulation.total_shards,
            )
            engine_result = _to_engine_result(aggregated, profile=profile)
            game = GameVersion.model_validate(game_version.canonical_json)
            report = _build_aggregate_mathematics_report(engine_result, game=game)

            results = SimulationResultRepository(session)
            await results.add(
                SimulationResultRow(
                    simulation_id=simulation.id,
                    total_bet_minor_units=engine_result.total_bet_minor_units,
                    total_win_minor_units=engine_result.total_win_minor_units,
                    uncapped_win_minor_units=engine_result.uncapped_win_minor_units,
                    rtp=report.rtp.rtp,
                    volatility=report.volatility.standard_deviation,
                    hit_frequency=report.hit_frequency.hit_frequency,
                    mathematics_report=report.model_dump(mode="json", by_alias=True),
                ),
            )
            simulation.status = SimulationStatus.COMPLETED
            simulation.completed_spin_count = simulation.spin_count
            simulation.completed_at = datetime.now(tz=UTC)
            simulation.progress_percentage = 100.0
            simulation.error_message = None
            await session.commit()
            log_simulation_event(
                "simulation_completed",
                simulation_id=str(simulation_id),
                spin_count=simulation.spin_count,
                distributed=True,
            )
            await notify_simulation_finished_by_id(self.session_factory, simulation_id)
            return True

    async def _mark_cancelled(
        self,
        simulations: SimulationRepository,
        simulation: Simulation,
    ) -> None:
        simulation.status = SimulationStatus.FAILED
        simulation.error_message = "Simulation cancelled"
        simulation.completed_at = datetime.now(tz=UTC)


def _to_engine_result(aggregated: PartialAccumulator, *, profile) -> SimulationResult:
    engine_version = profile.resolved_engine_version() or ENGINE_VERSION
    return SimulationResult(
        spinCount=profile.spin_count,
        shardCount=profile.shard_count,
        elapsedTimeMs=0,
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


def merge_partials(partials: list[PartialAccumulator]) -> PartialAccumulator:
    return AccumulatorAggregator.aggregate(tuple(partials))
