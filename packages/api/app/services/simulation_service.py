"""Simulation execution and retrieval service."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from runtime_core.domain.game_version import GameVersion
from runtime_core.mathematical.insights import enrich_mathematics_report
from runtime_core.mathematical.models import MathematicsReport

from app.config import Settings
from runtime_core.simulation.models import SimulationResult as EngineSimulationResult
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import AuthContext
from app.db.models.game import Game
from app.db.models.game_version import GameVersion
from app.db.models.organization_member import OrganizationRole
from app.db.models.simulation import Simulation, SimulationStatus
from app.db.models.simulation_note import SimulationNote
from app.db.models.simulation_result import SimulationResult
from app.db.repositories.game_repository import GameRepository
from app.db.repositories.game_version_repository import GameVersionRepository
from app.db.repositories.simulation_note_repository import SimulationNoteRepository
from app.db.repositories.simulation_repository import SimulationRepository
from app.db.repositories.simulation_result_repository import SimulationResultRepository
from app.exceptions.domain import (
    GameVersionReferenceNotFoundError,
    InvalidComparisonError,
    SimulationCancelNotAllowedError,
    SimulationNoteNotFoundError,
    SimulationNotFoundError,
    SimulationResultsNotReadyError,
)
from app.jobs.queue import SimulationQueue
from app.jobs.models import SimulationJob
from app.jobs.simulation_logging import log_simulation_event
from app.deployment.limits import resolve_deployment_limits, validate_simulation_create
from app.certification import CERTIFICATION_NOTICE
from app.observability.metrics import SIMULATIONS_TOTAL
from app.services.audit_service import AuditService
from app.workbench.throughput import resolve_throughput
from app.schemas.simulations import (
    CancelSimulationResponse,
    ComparisonConfidenceIntervalItem,
    ComparisonFeatureFrequencyItem,
    ComparisonMetricItem,
    ComparisonRtpDecompositionItem,
    ConfidenceIntervalSummary,
    CreateSimulationNoteRequest,
    CreateSimulationRequest,
    CreateSimulationResponse,
    ExposureSummary,
    FeatureFrequencyItem,
    FeatureValidationItem,
    HitFrequencySummary,
    JackpotFrequencyItem,
    RecommendationItem,
    RtpDecompositionChartSummary,
    RtpDecompositionSummary,
    RtpValidationSummary,
    SimulationCompareEntry,
    SimulationCompareResponse,
    SimulationComparisonMetrics,
    SimulationDetailResponse,
    SimulationListResponse,
    SimulationNoteListResponse,
    SimulationNoteResponse,
    SimulationProgress,
    SimulationResultsResponse,
    SimulationResultsSummary,
    SimulationResultsTotals,
    SimulationSummaryResponse,
    SimulationThroughputResponse,
    VolatilityMetricsSummary,
    WinDistributionSummary,
)

MAX_COMPARE_SIMULATIONS = 5
MIN_COMPARE_SIMULATIONS = 2


def _progress_for(simulation: Simulation) -> SimulationProgress:
    spin_count = simulation.spin_count
    completed = simulation.completed_spin_count
    if spin_count <= 0:
        percentage = 100.0
    else:
        percentage = min(100.0, (completed / spin_count) * 100.0)
    return SimulationProgress(
        completed_spins=completed,
        percentage=percentage,
    )


def _to_summary(simulation: Simulation) -> SimulationSummaryResponse:
    return SimulationSummaryResponse(
        id=simulation.id,
        game_version_id=simulation.game_version_id,
        status=simulation.status.value,
        spin_count=simulation.spin_count,
        completed_spin_count=simulation.completed_spin_count,
        created_at=simulation.created_at,
        completed_at=simulation.completed_at,
        error_message=simulation.error_message,
    )


def _to_detail(simulation: Simulation) -> SimulationDetailResponse:
    progress = _progress_for(simulation)
    if simulation.distributed_execution and simulation.total_shards > 0:
        progress = SimulationProgress(
            completed_spins=simulation.completed_spin_count,
            percentage=simulation.progress_percentage,
        )
    return SimulationDetailResponse(
        id=simulation.id,
        game_version_id=simulation.game_version_id,
        status=simulation.status.value,
        spin_count=simulation.spin_count,
        completed_spin_count=simulation.completed_spin_count,
        bet_minor_units=simulation.bet_minor_units,
        event_log_mode=simulation.event_log_mode,
        created_at=simulation.created_at,
        started_at=simulation.started_at,
        completed_at=simulation.completed_at,
        cancel_requested=simulation.cancel_requested,
        worker_id=simulation.worker_id,
        error_message=simulation.error_message,
        progress=progress,
        total_shards=simulation.total_shards,
        completed_shards=simulation.completed_shards,
        failed_shards=simulation.failed_shards,
        progress_percentage=simulation.progress_percentage,
        distributed_execution=simulation.distributed_execution,
    )


def _parse_mathematics_report(raw: dict) -> MathematicsReport:
    return MathematicsReport.model_validate(raw)


def _reconstruct_engine_result(
    db_result: SimulationResult,
    report: MathematicsReport,
) -> EngineSimulationResult:
    feature_counts = {
        item.feature_name: item.trigger_count for item in report.feature_frequencies
    }
    jackpot_counts = {
        item.jackpot_tier: item.trigger_count for item in report.jackpot_frequencies
    }
    win_by_category = {
        item.rtp_category: item.win_minor_units for item in report.rtp_decomposition.categories
    }
    return EngineSimulationResult(
        spinCount=report.spin_count,
        shardCount=1,
        elapsedTimeMs=0,
        totalBetMinorUnits=db_result.total_bet_minor_units,
        totalWinMinorUnits=db_result.total_win_minor_units,
        uncappedWinMinorUnits=db_result.uncapped_win_minor_units,
        exposureTruncationCount=0,
        exposureTruncatedMinorUnits=report.exposure.total_truncated_minor_units,
        chainFaultCount=0,
        limitHitCount=0,
        featureTriggerCounts=feature_counts,
        jackpotCounts=jackpot_counts,
        winByRtpCategoryMinorUnits=win_by_category,
        nestedFeatureEntries=0,
        eventSampleCount=0,
        engineVersion=report.engine_version,
    )


async def _ensure_insights_enriched(
    service: SimulationService,
    simulation: Simulation,
    db_result: SimulationResult,
    report: MathematicsReport,
) -> MathematicsReport:
    if report.rtp_validation is not None:
        return report

    game_version = await service.game_versions.get_by_id(simulation.game_version_id)
    if game_version is None:
        return report

    game = GameVersion.model_validate(game_version.canonical_json)
    engine_result = _reconstruct_engine_result(db_result, report)
    return enrich_mathematics_report(report, game=game, result=engine_result)


def _to_results_response(
    simulation_id: uuid.UUID,
    db_result: SimulationResult,
    report: MathematicsReport,
    *,
    game_version_content_hash: str,
) -> SimulationResultsResponse:
    rtp = report.rtp
    hit_frequency = report.hit_frequency
    volatility = report.volatility
    exposure = report.exposure
    chart = report.rtp_decomposition_chart

    rtp_validation = None
    if report.rtp_validation is not None:
        rtp_validation = RtpValidationSummary.model_validate(
            report.rtp_validation.model_dump(by_alias=True),
        )

    exposure_payload = exposure.model_dump(by_alias=True)
    exposure_payload["exposureCapApplied"] = (
        exposure.truncation_rate > 0 or exposure.total_truncated_minor_units > 0
    )

    return SimulationResultsResponse(
        simulation_id=simulation_id,
        summary=SimulationResultsSummary(
            rtp=rtp.rtp,
            uncapped_rtp=rtp.uncapped_rtp,
            volatility=volatility.standard_deviation,
            hit_frequency=hit_frequency.hit_frequency,
        ),
        totals=SimulationResultsTotals(
            total_bet_minor_units=db_result.total_bet_minor_units,
            total_win_minor_units=db_result.total_win_minor_units,
        ),
        feature_frequencies=[
            FeatureFrequencyItem.model_validate(item.model_dump(by_alias=True))
            for item in report.feature_frequencies
        ],
        jackpot_frequencies=[
            JackpotFrequencyItem.model_validate(item.model_dump(by_alias=True))
            for item in report.jackpot_frequencies
        ],
        exposure=ExposureSummary.model_validate(exposure_payload),
        rtp_decomposition=RtpDecompositionSummary.model_validate(
            report.rtp_decomposition.model_dump(by_alias=True),
        ),
        rtp_validation=rtp_validation,
        rtp_decomposition_chart=RtpDecompositionChartSummary(
            base=chart.base,
            free_spins=chart.free_spins,
            hold_and_win=chart.hold_and_win,
            jackpot=chart.jackpot,
            total_rtp=chart.total_rtp,
        ),
        feature_validation=[
            FeatureValidationItem.model_validate(item.model_dump(by_alias=True))
            for item in report.feature_validation
        ],
        recommendations=[
            RecommendationItem.model_validate(item.model_dump(by_alias=True))
            for item in report.recommendations
        ],
        confidence_interval=ConfidenceIntervalSummary(
            rtp=rtp.rtp,
            lower_bound=report.confidence_interval.lower_bound,
            upper_bound=report.confidence_interval.upper_bound,
            confidence_level=report.confidence_interval.confidence_level,
        ),
        win_distribution=WinDistributionSummary.model_validate(
            report.win_distribution.model_dump(by_alias=True),
        ),
        volatility_metrics=VolatilityMetricsSummary.model_validate(
            volatility.model_dump(by_alias=True),
        ),
        hit_frequency=HitFrequencySummary.model_validate(
            hit_frequency.model_dump(by_alias=True),
        ),
        engine_version=report.engine_version,
        game_version_content_hash=game_version_content_hash,
        certification_notice=CERTIFICATION_NOTICE,
        simulation_intelligence=(
            report.simulation_intelligence.model_dump(by_alias=True)
            if report.simulation_intelligence is not None
            else None
        ),
    )


def _runtime_duration_ms(simulation: Simulation) -> int | None:
    if simulation.started_at is None or simulation.completed_at is None:
        return None
    delta = simulation.completed_at - simulation.started_at
    return max(0, int(delta.total_seconds() * 1000))


def _build_comparison_metrics(
    entries: list[SimulationCompareEntry],
    reports: dict[uuid.UUID, MathematicsReport],
) -> SimulationComparisonMetrics:
    rtp_items: list[ComparisonMetricItem] = []
    volatility_items: list[ComparisonMetricItem] = []
    hit_frequency_items: list[ComparisonMetricItem] = []
    confidence_items: list[ComparisonConfidenceIntervalItem] = []
    feature_items: list[ComparisonFeatureFrequencyItem] = []
    decomposition_items: list[ComparisonRtpDecompositionItem] = []

    for entry in entries:
        sim_id = entry.simulation_id
        results = entry.results
        rtp_items.append(
            ComparisonMetricItem(simulation_id=sim_id, value=results.summary.rtp),
        )
        volatility_items.append(
            ComparisonMetricItem(
                simulation_id=sim_id,
                value=results.summary.volatility,
            ),
        )
        hit_frequency_items.append(
            ComparisonMetricItem(
                simulation_id=sim_id,
                value=results.summary.hit_frequency,
            ),
        )
        report = reports[sim_id]
        confidence_items.append(
            ComparisonConfidenceIntervalItem(
                simulation_id=sim_id,
                lower_bound=report.confidence_interval.lower_bound,
                upper_bound=report.confidence_interval.upper_bound,
                confidence_level=report.confidence_interval.confidence_level,
            ),
        )
        for feature in results.feature_frequencies:
            feature_items.append(
                ComparisonFeatureFrequencyItem(
                    simulation_id=sim_id,
                    feature_name=feature.feature_name,
                    frequency=feature.frequency,
                ),
            )
        chart = results.rtp_decomposition_chart
        decomposition_items.append(
            ComparisonRtpDecompositionItem(
                simulation_id=sim_id,
                base=chart.base,
                free_spins=chart.free_spins,
                hold_and_win=chart.hold_and_win,
                jackpot=chart.jackpot,
                total_rtp=chart.total_rtp,
            ),
        )

    return SimulationComparisonMetrics(
        rtp=rtp_items,
        volatility=volatility_items,
        hit_frequency=hit_frequency_items,
        confidence_intervals=confidence_items,
        feature_frequency=feature_items,
        rtp_decomposition=decomposition_items,
    )


def _to_note_response(note: SimulationNote) -> SimulationNoteResponse:
    return SimulationNoteResponse(
        id=note.id,
        simulation_id=note.simulation_id,
        author_id=note.author_id,
        content=note.content,
        created_at=note.created_at,
    )


@dataclass(frozen=True, slots=True)
class SimulationService:
    simulations: SimulationRepository
    simulation_results: SimulationResultRepository
    simulation_notes: SimulationNoteRepository
    game_versions: GameVersionRepository
    games: GameRepository
    queue: SimulationQueue | None = None
    settings: Settings | None = None

    @classmethod
    def from_session(
        cls,
        session: AsyncSession,
        *,
        queue: SimulationQueue | None = None,
        settings: Settings | None = None,
    ) -> SimulationService:
        return cls(
            simulations=SimulationRepository(session),
            simulation_results=SimulationResultRepository(session),
            simulation_notes=SimulationNoteRepository(session),
            game_versions=GameVersionRepository(session),
            games=GameRepository(session),
            queue=queue,
            settings=settings,
        )

    async def create_simulation(
        self,
        auth: AuthContext,
        body: CreateSimulationRequest,
    ) -> CreateSimulationResponse:
        game_version = await self.game_versions.get_by_id_for_organizations(
            body.game_version_id,
            auth.organization_ids,
        )
        if game_version is None:
            raise GameVersionReferenceNotFoundError(
                game_version_id=str(body.game_version_id),
            )

        game = await self.games.get_by_id_for_organizations(
            game_version.game_id,
            auth.organization_ids,
        )
        if game is None:
            raise GameVersionReferenceNotFoundError(
                game_version_id=str(body.game_version_id),
            )
        auth.require_role(game.organization_id, OrganizationRole.DEVELOPER)

        if self.settings is not None:
            limits = resolve_deployment_limits(self.settings)
            active_count = await self.simulations.count_active()
            validate_simulation_create(
                spin_count=body.spin_count,
                active_simulation_count=active_count,
                limits=limits,
            )

        simulation = Simulation(
            game_version_id=body.game_version_id,
            status=SimulationStatus.PENDING,
            spin_count=body.spin_count,
            completed_spin_count=0,
            bet_minor_units=body.bet_minor_units,
            event_log_mode=body.event_log_mode,
            master_seed=body.master_seed,
            cancel_requested=False,
            created_by_user_id=auth.user.id,
        )
        await self.simulations.add(simulation)
        SIMULATIONS_TOTAL.labels(status="pending").inc()

        audit = AuditService.from_session(self.simulations._session)
        await audit.record(
            action="simulation.create",
            entity_type="simulation",
            entity_id=simulation.id,
            user_id=auth.user.id,
            organization_id=game.organization_id,
            metadata={"spinCount": body.spin_count},
        )

        # Commit before enqueue so workers can see the persisted PENDING row.
        await self.simulations._session.commit()

        if self.queue is None:
            log_simulation_event(
                "simulation_enqueue_skipped_no_dispatcher",
                simulation_id=str(simulation.id),
            )
        else:
            log_simulation_event(
                "simulation_service_enqueue",
                simulation_id=str(simulation.id),
                queue_id=id(self.queue),
            )
            await self.queue.enqueue(SimulationJob(simulation_id=simulation.id))

        return CreateSimulationResponse(
            simulation_id=simulation.id,
            status=simulation.status.value,
        )

    async def cancel_simulation(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
    ) -> CancelSimulationResponse:
        simulation = await self._require_simulation(auth, simulation_id)
        if simulation.status not in (
            SimulationStatus.PENDING,
            SimulationStatus.RUNNING,
        ):
            raise SimulationCancelNotAllowedError(
                simulation_id=str(simulation_id),
                status=simulation.status.value,
            )

        game_version = await self.game_versions.get_by_id(simulation.game_version_id)
        if game_version is not None:
            game = await self.games.get_by_id_for_organizations(
                game_version.game_id,
                auth.organization_ids,
            )
            if game is not None:
                auth.require_role(game.organization_id, OrganizationRole.DEVELOPER)

        simulation.cancel_requested = True
        await self.simulations.save(simulation)

        if simulation.distributed_execution:
            from app.db.repositories.simulation_shard_repository import SimulationShardRepository
            from app.db.models.simulation_shard import SimulationShardStatus
            from app.distributed.celery_app import celery_app

            shards = SimulationShardRepository(self.simulations._session)
            task_ids: list[str] = []
            for shard in await shards.list_by_simulation_id(simulation_id):
                if shard.status in {
                    SimulationShardStatus.PENDING,
                    SimulationShardStatus.RUNNING,
                }:
                    shard.status = SimulationShardStatus.CANCELLED
                    shard.completed_at = datetime.now(tz=UTC)
                    if shard.celery_task_id:
                        task_ids.append(shard.celery_task_id)
            await self.simulations._session.commit()
            for task_id in task_ids:
                celery_app.control.revoke(task_id, terminate=True)

        return CancelSimulationResponse(
            simulation_id=simulation.id,
            status=simulation.status.value,
            cancel_requested=True,
        )

    async def list_simulations(
        self,
        auth: AuthContext,
        *,
        page: int,
        page_size: int,
        status: str | None,
        game_version_id: uuid.UUID | None,
    ) -> SimulationListResponse:
        parsed_status = _parse_status_filter(status)
        organization_ids = auth.organization_ids
        total = await self.simulations.count_filtered(
            status=parsed_status,
            game_version_id=game_version_id,
            organization_ids=organization_ids,
        )
        items = await self.simulations.search_paginated(
            page=page,
            page_size=page_size,
            status=parsed_status,
            game_version_id=game_version_id,
            organization_ids=organization_ids,
        )
        return SimulationListResponse(
            items=[_to_summary(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_simulation(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
    ) -> SimulationDetailResponse:
        simulation = await self._require_simulation(auth, simulation_id)
        return _to_detail(simulation)

    async def get_simulation_results(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
    ) -> SimulationResultsResponse:
        simulation = await self._require_simulation(auth, simulation_id)
        if simulation.status != SimulationStatus.COMPLETED:
            raise SimulationResultsNotReadyError(
                simulation_id=str(simulation_id),
                status=simulation.status.value,
            )

        result = await self.simulation_results.get_by_simulation_id(simulation_id)
        if result is None:
            raise SimulationResultsNotReadyError(
                simulation_id=str(simulation_id),
                status=simulation.status.value,
            )

        report = _parse_mathematics_report(result.mathematics_report)
        report = await _ensure_insights_enriched(self, simulation, result, report)
        game_version = await self.game_versions.get_by_id(simulation.game_version_id)
        content_hash = game_version.content_hash if game_version is not None else ""
        return _to_results_response(
            simulation_id,
            result,
            report,
            game_version_content_hash=content_hash,
        )

    async def compare_simulations(
        self,
        auth: AuthContext,
        simulation_ids: list[uuid.UUID],
    ) -> SimulationCompareResponse:
        if len(simulation_ids) < MIN_COMPARE_SIMULATIONS:
            raise InvalidComparisonError(
                message="at least two simulation ids are required for comparison",
                details={"minCount": MIN_COMPARE_SIMULATIONS},
            )
        if len(simulation_ids) > MAX_COMPARE_SIMULATIONS:
            raise InvalidComparisonError(
                message=f"at most {MAX_COMPARE_SIMULATIONS} simulations can be compared",
                details={"maxCount": MAX_COMPARE_SIMULATIONS},
            )
        if len(set(simulation_ids)) != len(simulation_ids):
            raise InvalidComparisonError(
                message="duplicate simulation ids are not allowed",
            )

        organization_ids: set[uuid.UUID] = set()
        simulations: list[Simulation] = []
        for simulation_id in simulation_ids:
            simulation = await self.simulations.get_by_id_for_organizations(
                simulation_id,
                auth.organization_ids,
            )
            if simulation is None:
                raise SimulationNotFoundError(simulation_id=str(simulation_id))
            if simulation.status != SimulationStatus.COMPLETED:
                raise InvalidComparisonError(
                    message="all simulations must be completed",
                    details={
                        "simulationId": str(simulation_id),
                        "status": simulation.status.value,
                    },
                )
            org_id = await self.simulations.get_organization_id(simulation_id)
            if org_id is None:
                raise SimulationNotFoundError(simulation_id=str(simulation_id))
            organization_ids.add(org_id)
            simulations.append(simulation)

        if len(organization_ids) > 1:
            raise InvalidComparisonError(
                message="all simulations must belong to the same organization",
            )

        entries: list[SimulationCompareEntry] = []
        reports: dict[uuid.UUID, MathematicsReport] = {}
        for simulation in simulations:
            db_result = await self.simulation_results.get_by_simulation_id(simulation.id)
            if db_result is None:
                raise SimulationResultsNotReadyError(
                    simulation_id=str(simulation.id),
                    status=simulation.status.value,
                )
            report = _parse_mathematics_report(db_result.mathematics_report)
            report = await _ensure_insights_enriched(
                self,
                simulation,
                db_result,
                report,
            )
            reports[simulation.id] = report
            game_version = await self.game_versions.get_by_id(simulation.game_version_id)
            content_hash = game_version.content_hash if game_version is not None else ""
            game_name = None
            game_version_label = None
            if game_version is not None:
                game_version_label = f"v{game_version.version}"
                game = await self.games.get_by_id(game_version.game_id)
                if game is not None:
                    game_name = game.name
            entries.append(
                SimulationCompareEntry(
                    simulation_id=simulation.id,
                    game_name=game_name,
                    game_version_label=game_version_label,
                    detail=_to_detail(simulation),
                    results=_to_results_response(
                        simulation.id,
                        db_result,
                        report,
                        game_version_content_hash=content_hash,
                    ),
                    runtime_duration_ms=_runtime_duration_ms(simulation),
                ),
            )

        return SimulationCompareResponse(
            simulations=entries,
            comparison=_build_comparison_metrics(entries, reports),
        )

    async def get_throughput(self, auth: AuthContext) -> SimulationThroughputResponse:
        if self.settings is None:
            msg = "application settings not configured"
            raise RuntimeError(msg)
        result = await self.simulations._session.scalars(
            select(Simulation)
            .join(GameVersion, Simulation.game_version_id == GameVersion.id)
            .join(Game, GameVersion.game_id == Game.id)
            .where(
                Game.organization_id.in_(auth.organization_ids),
                Simulation.status == SimulationStatus.COMPLETED,
            )
            .order_by(Simulation.completed_at.desc())
            .limit(50),
        )
        estimate = resolve_throughput(list(result.all()), self.settings)
        return SimulationThroughputResponse(
            spins_per_second=estimate.spins_per_second,
            sample_count=estimate.sample_count,
            source=estimate.source,
        )

    async def list_simulation_notes(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
    ) -> SimulationNoteListResponse:
        await self._require_simulation(auth, simulation_id)
        notes = await self.simulation_notes.list_by_simulation_id(simulation_id)
        return SimulationNoteListResponse(
            items=[_to_note_response(note) for note in notes],
        )

    async def create_simulation_note(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
        body: CreateSimulationNoteRequest,
    ) -> SimulationNoteResponse:
        simulation = await self._require_simulation(auth, simulation_id)
        await self._require_developer_for_simulation(auth, simulation)
        note = SimulationNote(
            simulation_id=simulation_id,
            author_id=auth.user_id,
            content=body.content.strip(),
        )
        await self.simulation_notes.add(note)
        return _to_note_response(note)

    async def delete_simulation_note(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
        note_id: uuid.UUID,
    ) -> None:
        simulation = await self._require_simulation(auth, simulation_id)
        await self._require_developer_for_simulation(auth, simulation)
        note = await self.simulation_notes.get_by_id_for_simulation(
            note_id,
            simulation_id,
        )
        if note is None:
            raise SimulationNoteNotFoundError(
                simulation_id=str(simulation_id),
                note_id=str(note_id),
            )
        await self.simulation_notes.delete(note)

    async def list_simulation_shards(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
    ):
        from app.db.repositories.simulation_shard_repository import SimulationShardRepository
        from app.schemas.distributed import SimulationShardListResponse, SimulationShardResponse

        simulation = await self._require_simulation(auth, simulation_id)
        shards = await SimulationShardRepository(
            self.simulations._session,
        ).list_by_simulation_id(simulation_id)
        return SimulationShardListResponse(
            items=[
                SimulationShardResponse(
                    id=shard.id,
                    simulation_id=shard.simulation_id,
                    shard_index=shard.shard_index,
                    spin_count=shard.spin_count,
                    status=shard.status.value,
                    worker_id=shard.worker_id,
                    started_at=shard.started_at,
                    completed_at=shard.completed_at,
                    error_message=shard.error_message,
                )
                for shard in shards
            ],
            total_shards=simulation.total_shards,
            completed_shards=simulation.completed_shards,
            failed_shards=simulation.failed_shards,
            progress_percentage=simulation.progress_percentage,
        )

    async def retry_failed_shards(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
    ):
        from app.config import get_settings
        from app.db.session import create_session_factory
        from app.distributed.orchestration_service import OrchestrationService
        from app.exceptions.domain import ForbiddenError
        from app.schemas.distributed import RetrySimulationResponse

        simulation = await self._require_simulation(auth, simulation_id)
        await self._require_developer_for_simulation(auth, simulation)
        if not simulation.distributed_execution:
            raise ForbiddenError(message="retry is only available for distributed simulations")
        if simulation.failed_shards <= 0:
            return RetrySimulationResponse(simulation_id=simulation_id, retried_shards=0)

        engine = self.simulations._session.get_bind()
        factory = create_session_factory(engine)
        orchestrator = OrchestrationService(factory, get_settings())
        retried = await orchestrator.retry_failed(simulation_id)
        return RetrySimulationResponse(simulation_id=simulation_id, retried_shards=retried)

    async def _require_developer_for_simulation(
        self,
        auth: AuthContext,
        simulation: Simulation,
    ) -> None:
        org_id = await self.simulations.get_organization_id(simulation.id)
        if org_id is None:
            raise SimulationNotFoundError(simulation_id=str(simulation.id))
        auth.require_role(org_id, OrganizationRole.DEVELOPER)

    async def _require_simulation(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
    ) -> Simulation:
        simulation = await self.simulations.get_by_id_for_organizations(
            simulation_id,
            auth.organization_ids,
        )
        if simulation is None:
            raise SimulationNotFoundError(simulation_id=str(simulation_id))
        return simulation


def _parse_status_filter(status: str | None) -> SimulationStatus | None:
    if status is None:
        return None
    try:
        return SimulationStatus(status)
    except ValueError as exc:
        msg = f"unsupported status filter {status!r}"
        raise ValueError(msg) from exc
