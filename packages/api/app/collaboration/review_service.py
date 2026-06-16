"""Simulation review service."""

from __future__ import annotations

import uuid

from app.auth.context import AuthContext
from app.collaboration.activity_service import ActivityService
from app.db.models.simulation import Simulation
from app.db.models.simulation_review import SimulationReview
from app.db.models.simulation_workflow import ReviewStatus, SimulationWorkflowStatus
from app.db.repositories.simulation_repository import SimulationRepository
from app.db.repositories.simulation_review_repository import SimulationReviewRepository
from app.exceptions.domain import ForbiddenError, ReviewDecisionRequiredError
from app.security.permissions import role_at_least
from app.db.models.organization_member import OrganizationRole
from app.services.notification_service import NotificationService


class ReviewService:
    def __init__(
        self,
        reviews: SimulationReviewRepository,
        simulations: SimulationRepository,
        activity: ActivityService,
        notifications: NotificationService,
    ) -> None:
        self._reviews = reviews
        self._simulations = simulations
        self._activity = activity
        self._notifications = notifications

    async def submit_review(
        self,
        auth: AuthContext,
        simulation: Simulation,
        org_id: uuid.UUID,
        *,
        status: ReviewStatus,
        decision_reason: str | None,
    ) -> SimulationReview:
        role = auth.memberships.get(org_id, OrganizationRole.VIEWER)
        if not role_at_least(role, OrganizationRole.ADMIN):
            raise ForbiddenError(message="insufficient permissions to review simulation")

        if status in {ReviewStatus.REJECTED, ReviewStatus.CHANGES_REQUESTED}:
            reason = (decision_reason or "").strip()
            if not reason:
                raise ReviewDecisionRequiredError(status=status.value)

        review = SimulationReview(
            simulation_id=simulation.id,
            reviewer_id=auth.user_id,
            status=status,
            decision_reason=decision_reason,
        )
        await self._reviews.add(review)

        if status == ReviewStatus.CHANGES_REQUESTED:
            simulation.workflow_status = SimulationWorkflowStatus.DRAFT
            await self._activity.record(
                simulation_id=simulation.id,
                actor_id=auth.user_id,
                action="changes_requested",
                metadata={"reviewId": str(review.id), "reason": decision_reason},
            )
            if simulation.created_by_user_id:
                await self._notifications.create_collaboration_notification(
                    user_id=simulation.created_by_user_id,
                    organization_id=org_id,
                    notification_type="changes_requested",
                    title="Changes requested",
                    message=f"Changes were requested for simulation {simulation.id}.",
                    entity_id=simulation.id,
                )
        elif status == ReviewStatus.APPROVED:
            simulation.workflow_status = SimulationWorkflowStatus.APPROVED
            await self._activity.record(
                simulation_id=simulation.id,
                actor_id=auth.user_id,
                action="review_approved",
                metadata={"reviewId": str(review.id)},
            )
            if simulation.created_by_user_id:
                await self._notifications.create_collaboration_notification(
                    user_id=simulation.created_by_user_id,
                    organization_id=org_id,
                    notification_type="simulation_approved",
                    title="Simulation approved",
                    message=f"Simulation {simulation.id} was approved.",
                    entity_id=simulation.id,
                )
        elif status == ReviewStatus.REJECTED:
            simulation.workflow_status = SimulationWorkflowStatus.DRAFT
            await self._activity.record(
                simulation_id=simulation.id,
                actor_id=auth.user_id,
                action="review_rejected",
                metadata={"reviewId": str(review.id), "reason": decision_reason},
            )

        return review

    async def list_reviews(self, simulation_id: uuid.UUID) -> list[SimulationReview]:
        return await self._reviews.list_by_simulation_id(simulation_id)
