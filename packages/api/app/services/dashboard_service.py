"""Dashboard aggregate queries."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import AuthContext
from app.db.models.game import Game
from app.db.models.game_version import GameVersion
from app.db.models.organization_member import OrganizationRole
from app.db.models.simulation import Simulation, SimulationStatus
from app.db.models.simulation_result import SimulationResult
from app.db.models.simulation_workflow import SimulationWorkflowStatus
from app.schemas.collaboration import CollaborationSimulationSummary
from app.schemas.platform import (
    DashboardRecommendedAction,
    DashboardSimulationSummary,
    DashboardSummaryResponse,
)
from app.services.audit_service import AuditService, _to_audit_response
from app.services.notification_service import (
    NotificationService,
    _to_notification_response,
)
from app.security.permissions import role_at_least


@dataclass(frozen=True, slots=True)
class DashboardService:
    session: AsyncSession

    @classmethod
    def from_session(cls, session: AsyncSession) -> DashboardService:
        return cls(session=session)

    async def get_summary(self, auth: AuthContext) -> DashboardSummaryResponse:
        org_ids = auth.organization_ids

        total_games = int(
            await self.session.scalar(
                select(func.count())
                .select_from(Game)
                .where(Game.organization_id.in_(org_ids)),
            )
            or 0,
        )
        total_simulations = int(
            await self.session.scalar(select(func.count()).select_from(Simulation))
            or 0,
        )
        active_simulations = int(
            await self.session.scalar(
                select(func.count())
                .select_from(Simulation)
                .where(
                    Simulation.status.in_(
                        [SimulationStatus.PENDING, SimulationStatus.RUNNING],
                    ),
                ),
            )
            or 0,
        )
        average_rtp = await self.session.scalar(
            select(func.avg(SimulationResult.rtp)).select_from(SimulationResult),
        )

        notifications = NotificationService.from_session(self.session)
        recent_items, _ = await notifications.notifications.list_for_user(
            auth.user_id,
            notification_type=None,
            unread_only=False,
            page=1,
            page_size=5,
        )

        audit = AuditService.from_session(self.session)
        activity_items, _ = await audit.audit_logs.list_filtered(
            org_ids,
            user_id=None,
            action=None,
            date_from=None,
            date_to=None,
            page=1,
            page_size=5,
        )
        activity_responses = []
        for item in activity_items:
            user = (
                await audit.users.get_by_id(item.user_id)
                if item.user_id is not None
                else None
            )
            activity_responses.append(
                _to_audit_response(
                    item,
                    user.email if user else None,
                    user.full_name if user else None,
                ),
            )

        pending_reviews = await self._list_workflow_simulations(
            org_ids,
            SimulationWorkflowStatus.UNDER_REVIEW,
            limit=5,
        )
        reviewer_org_ids = [
            org_id
            for org_id in org_ids
            if role_at_least(
                auth.memberships.get(org_id, OrganizationRole.VIEWER),
                OrganizationRole.ADMIN,
            )
        ]
        my_pending_reviews = await self._list_workflow_simulations(
            reviewer_org_ids,
            SimulationWorkflowStatus.UNDER_REVIEW,
            limit=5,
        )
        certification_ready = await self._list_workflow_simulations(
            org_ids,
            SimulationWorkflowStatus.CERTIFICATION_READY,
            limit=5,
        )
        recently_approved = await self._list_workflow_simulations(
            org_ids,
            SimulationWorkflowStatus.APPROVED,
            limit=5,
        )
        recent_simulations = await self._list_recent_simulations(org_ids, limit=5)
        outside_rtp_tolerance = await self._list_outside_rtp_tolerance(org_ids, limit=5)
        recommended_actions = self._build_recommended_actions(
            pending_reviews=pending_reviews,
            certification_ready=certification_ready,
            outside_rtp_tolerance=outside_rtp_tolerance,
        )

        return DashboardSummaryResponse(
            total_games=total_games,
            total_simulations=total_simulations,
            active_simulations=active_simulations,
            average_rtp=float(average_rtp) if average_rtp is not None else None,
            recent_notifications=[
                _to_notification_response(item) for item in recent_items
            ],
            recent_activity=activity_responses,
            pending_reviews=pending_reviews,
            my_pending_reviews=my_pending_reviews,
            certification_ready=certification_ready,
            recently_approved=recently_approved,
            recent_simulations=recent_simulations,
            outside_rtp_tolerance=outside_rtp_tolerance,
            recommended_actions=recommended_actions,
        )

    def _build_recommended_actions(
        self,
        *,
        pending_reviews: list[CollaborationSimulationSummary],
        certification_ready: list[CollaborationSimulationSummary],
        outside_rtp_tolerance: list[DashboardSimulationSummary],
    ) -> list[DashboardRecommendedAction]:
        actions: list[DashboardRecommendedAction] = []
        if pending_reviews:
            actions.append(
                DashboardRecommendedAction(
                    id="pending-reviews",
                    label="Review pending simulations",
                    description=f"{len(pending_reviews)} simulation(s) await mathematician review.",
                    href="/simulations",
                ),
            )
        if outside_rtp_tolerance:
            actions.append(
                DashboardRecommendedAction(
                    id="rtp-drift",
                    label="Investigate RTP drift",
                    description=(
                        f"{len(outside_rtp_tolerance)} completed simulation(s) "
                        "are outside configured RTP tolerance."
                    ),
                    href="/simulations",
                ),
            )
        if certification_ready:
            actions.append(
                DashboardRecommendedAction(
                    id="certification-ready",
                    label="Finalize certification",
                    description=(
                        f"{len(certification_ready)} simulation(s) are ready for certification."
                    ),
                    href="/simulations",
                ),
            )
        if not actions:
            actions.append(
                DashboardRecommendedAction(
                    id="run-simulation",
                    label="Run a calibration simulation",
                    description="Upload a game version and start a 100K-spin simulation.",
                    href="/simulations/create",
                ),
            )
        return actions

    async def _list_recent_simulations(
        self,
        org_ids: list,
        *,
        limit: int,
    ) -> list[DashboardSimulationSummary]:
        rows = await self.session.execute(
            select(Simulation, SimulationResult, Game, GameVersion)
            .join(GameVersion, Simulation.game_version_id == GameVersion.id)
            .join(Game, GameVersion.game_id == Game.id)
            .outerjoin(SimulationResult, SimulationResult.simulation_id == Simulation.id)
            .where(Game.organization_id.in_(org_ids))
            .order_by(Simulation.created_at.desc())
            .limit(limit),
        )
        return [
            self._to_dashboard_simulation_summary(
                simulation,
                result,
                game,
                game_version,
            )
            for simulation, result, game, game_version in rows.all()
        ]

    async def _list_outside_rtp_tolerance(
        self,
        org_ids: list,
        *,
        limit: int,
    ) -> list[DashboardSimulationSummary]:
        rows = await self.session.execute(
            select(Simulation, SimulationResult, Game, GameVersion)
            .join(SimulationResult, SimulationResult.simulation_id == Simulation.id)
            .join(GameVersion, Simulation.game_version_id == GameVersion.id)
            .join(Game, GameVersion.game_id == Game.id)
            .where(
                Game.organization_id.in_(org_ids),
                Simulation.status == SimulationStatus.COMPLETED,
            )
            .order_by(Simulation.completed_at.desc())
            .limit(limit * 4),
        )
        summaries: list[DashboardSimulationSummary] = []
        for simulation, result, game, game_version in rows.all():
            within = self._within_rtp_tolerance(result)
            if within is False:
                summaries.append(
                    self._to_dashboard_simulation_summary(
                        simulation,
                        result,
                        game,
                        game_version,
                    ),
                )
            if len(summaries) >= limit:
                break
        return summaries

    @staticmethod
    def _within_rtp_tolerance(result: SimulationResult | None) -> bool | None:
        if result is None:
            return None
        validation = result.mathematics_report.get("rtpValidation")
        if not isinstance(validation, dict):
            return None
        within = validation.get("withinTolerance")
        if isinstance(within, bool):
            return within
        return None

    @staticmethod
    def _to_dashboard_simulation_summary(
        simulation: Simulation,
        result: SimulationResult | None,
        game: Game,
        game_version: GameVersion,
    ) -> DashboardSimulationSummary:
        return DashboardSimulationSummary(
            simulation_id=simulation.id,
            game_version_id=simulation.game_version_id,
            game_name=game.name,
            game_version_label=f"v{game_version.version}",
            status=simulation.status.value,
            workflow_status=simulation.workflow_status.value,
            spin_count=simulation.spin_count,
            rtp=result.rtp if result is not None else None,
            within_rtp_tolerance=DashboardService._within_rtp_tolerance(result),
            created_at=simulation.created_at,
        )

    async def _list_workflow_simulations(
        self,
        org_ids: list,
        workflow_status: SimulationWorkflowStatus,
        *,
        limit: int,
    ) -> list[CollaborationSimulationSummary]:
        result = await self.session.scalars(
            select(Simulation)
            .join(GameVersion, Simulation.game_version_id == GameVersion.id)
            .join(Game, GameVersion.game_id == Game.id)
            .where(
                Game.organization_id.in_(org_ids),
                Simulation.workflow_status == workflow_status,
            )
            .order_by(Simulation.created_at.desc())
            .limit(limit),
        )
        return [
            CollaborationSimulationSummary(
                simulation_id=simulation.id,
                workflow_status=simulation.workflow_status.value,
                game_version_id=simulation.game_version_id,
                updated_at=simulation.created_at,
            )
            for simulation in result.all()
        ]
