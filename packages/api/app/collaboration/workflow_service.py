"""Simulation collaboration workflow service."""

from __future__ import annotations

import uuid

from app.auth.context import AuthContext
from app.collaboration.activity_service import ActivityService
from app.collaboration.permissions import can_request_review, can_transition
from app.db.models.organization_member import OrganizationMember, OrganizationRole
from app.db.models.simulation import Simulation
from app.db.models.simulation_review import SimulationReview
from app.db.models.simulation_workflow import ReviewStatus, SimulationWorkflowStatus
from app.db.repositories.organization_member_repository import OrganizationMemberRepository
from app.db.repositories.simulation_review_repository import SimulationReviewRepository
from app.exceptions.domain import ForbiddenError, InvalidWorkflowTransitionError
from app.services.notification_service import NotificationService


class WorkflowService:
    def __init__(
        self,
        reviews: SimulationReviewRepository,
        members: OrganizationMemberRepository,
        activity: ActivityService,
        notifications: NotificationService,
    ) -> None:
        self._reviews = reviews
        self._members = members
        self._activity = activity
        self._notifications = notifications

    def get_status(self, simulation: Simulation) -> SimulationWorkflowStatus:
        return simulation.workflow_status

    async def transition(
        self,
        auth: AuthContext,
        simulation: Simulation,
        org_id: uuid.UUID,
        *,
        target: SimulationWorkflowStatus,
    ) -> Simulation:
        current = simulation.workflow_status
        role = auth.memberships.get(org_id, OrganizationRole.VIEWER)
        if not can_transition(role, current, target):
            raise InvalidWorkflowTransitionError(
                current=current.value,
                target=target.value,
            )

        simulation.workflow_status = target
        await self._activity.record(
            simulation_id=simulation.id,
            actor_id=auth.user_id,
            action="workflow_transition",
            metadata={"from": current.value, "to": target.value},
        )

        if current == SimulationWorkflowStatus.DRAFT and target == SimulationWorkflowStatus.UNDER_REVIEW:
            review = SimulationReview(
                simulation_id=simulation.id,
                reviewer_id=auth.user_id,
                status=ReviewStatus.PENDING,
            )
            await self._reviews.add(review)
            await self._notify_review_requested(simulation, org_id)

        if target == SimulationWorkflowStatus.CERTIFICATION_READY:
            await self._notifications.create_collaboration_notification(
                user_id=simulation.created_by_user_id,
                organization_id=org_id,
                notification_type="certification_ready",
                title="Certification ready",
                message=f"Simulation {simulation.id} is ready for certification.",
                entity_id=simulation.id,
            )

        return simulation

    async def _notify_review_requested(
        self,
        simulation: Simulation,
        org_id: uuid.UUID,
    ) -> None:
        admins = await self._members.list_for_organization(org_id)
        for member in admins:
            if member.role in {OrganizationRole.ADMIN, OrganizationRole.OWNER}:
                await self._notifications.create_collaboration_notification(
                    user_id=member.user_id,
                    organization_id=org_id,
                    notification_type="review_requested",
                    title="Review requested",
                    message=f"A review was requested for simulation {simulation.id}.",
                    entity_id=simulation.id,
                )
