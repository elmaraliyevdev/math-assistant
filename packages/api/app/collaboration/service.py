"""Simulation collaboration facade."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import AuthContext
from app.collaboration.activity_service import ActivityService
from app.collaboration.approval_service import ApprovalService
from app.collaboration.comments_service import CommentsService
from app.collaboration.review_service import ReviewService
from app.collaboration.workflow_service import WorkflowService
from app.db.models.simulation_workflow import ApprovalStage, ReviewStatus, SimulationWorkflowStatus
from app.db.repositories.organization_member_repository import OrganizationMemberRepository
from app.db.repositories.simulation_approval_repository import SimulationApprovalRepository
from app.db.repositories.simulation_activity_log_repository import (
    SimulationActivityLogRepository,
)
from app.db.repositories.simulation_comment_repository import SimulationCommentRepository
from app.db.repositories.simulation_repository import SimulationRepository
from app.db.repositories.simulation_review_repository import SimulationReviewRepository
from app.exceptions.domain import SimulationNotFoundError
from app.schemas.collaboration import (
    ApproveSimulationRequest,
    CreateSimulationCommentRequest,
    SimulationActivityListResponse,
    SimulationActivityResponse,
    SimulationApprovalListResponse,
    SimulationApprovalResponse,
    SimulationCommentListResponse,
    SimulationCommentResponse,
    SimulationReviewResponse,
    SimulationWorkflowResponse,
    SubmitSimulationReviewRequest,
    WorkflowTransitionRequest,
)
from app.db.repositories.user_repository import UserRepository


from app.services.notification_service import NotificationService


def _comment_response(
    comment,
    *,
    author_name: str | None = None,
    author_email: str | None = None,
    author_role: str | None = None,
) -> SimulationCommentResponse:
    return SimulationCommentResponse(
        id=comment.id,
        simulation_id=comment.simulation_id,
        user_id=comment.user_id,
        author_name=author_name,
        author_email=author_email,
        author_role=author_role,
        content=comment.content,
        created_at=comment.created_at,
    )


def _review_response(
    review,
    *,
    reviewer_name: str | None = None,
    reviewer_email: str | None = None,
    reviewer_role: str | None = None,
) -> SimulationReviewResponse:
    return SimulationReviewResponse(
        id=review.id,
        simulation_id=review.simulation_id,
        reviewer_id=review.reviewer_id,
        reviewer_name=reviewer_name,
        reviewer_email=reviewer_email,
        reviewer_role=reviewer_role,
        status=review.status.value,
        decision_reason=review.decision_reason,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


def _approval_response(approval) -> SimulationApprovalResponse:
    return SimulationApprovalResponse(
        id=approval.id,
        simulation_id=approval.simulation_id,
        approved_by=approval.approved_by,
        approval_stage=approval.approval_stage.value,
        approved_at=approval.approved_at,
    )


def _activity_response(entry) -> SimulationActivityResponse:
    return SimulationActivityResponse(
        id=entry.id,
        simulation_id=entry.simulation_id,
        actor_id=entry.actor_id,
        action=entry.action,
        metadata=entry.metadata_json,
        created_at=entry.created_at,
    )


@dataclass(frozen=True, slots=True)
class CollaborationService:
    simulations: SimulationRepository
    comments: CommentsService
    reviews: ReviewService
    approvals: ApprovalService
    workflow: WorkflowService
    activity: ActivityService
    users: UserRepository
    members: OrganizationMemberRepository

    @classmethod
    def from_session(cls, session: AsyncSession) -> CollaborationService:
        activity_repo = SimulationActivityLogRepository(session)
        activity = ActivityService(activity_repo)
        notifications = NotificationService.from_session(session)
        return cls(
            simulations=SimulationRepository(session),
            comments=CommentsService(SimulationCommentRepository(session), activity),
            reviews=ReviewService(
                SimulationReviewRepository(session),
                SimulationRepository(session),
                activity,
                notifications,
            ),
            approvals=ApprovalService(SimulationApprovalRepository(session), activity),
            workflow=WorkflowService(
                SimulationReviewRepository(session),
                OrganizationMemberRepository(session),
                activity,
                notifications,
            ),
            activity=activity,
            users=UserRepository(session),
            members=OrganizationMemberRepository(session),
        )

    async def _require_simulation(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
    ):
        simulation = await self.simulations.get_by_id_for_organizations(
            simulation_id,
            auth.organization_ids,
        )
        if simulation is None:
            raise SimulationNotFoundError(simulation_id=str(simulation_id))
        return simulation

    async def _org_id(self, simulation_id: uuid.UUID) -> uuid.UUID:
        org_id = await self.simulations.get_organization_id(simulation_id)
        if org_id is None:
            raise SimulationNotFoundError(simulation_id=str(simulation_id))
        return org_id

    async def _author_metadata(
        self,
        user_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> tuple[str | None, str | None, str | None]:
        user = await self.users.get_by_id(user_id)
        membership = await self.members.get_membership(
            organization_id=org_id,
            user_id=user_id,
        )
        return (
            user.full_name if user else None,
            user.email if user else None,
            membership.role.value if membership else None,
        )

    async def list_comments(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
    ) -> SimulationCommentListResponse:
        await self._require_simulation(auth, simulation_id)
        org_id = await self._org_id(simulation_id)
        items = await self.comments.list_comments(simulation_id)
        responses = []
        for item in items:
            author_name, author_email, author_role = await self._author_metadata(
                item.user_id,
                org_id,
            )
            responses.append(
                _comment_response(
                    item,
                    author_name=author_name,
                    author_email=author_email,
                    author_role=author_role,
                ),
            )
        return SimulationCommentListResponse(items=responses)

    async def add_comment(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
        body: CreateSimulationCommentRequest,
    ) -> SimulationCommentResponse:
        simulation = await self._require_simulation(auth, simulation_id)
        org_id = await self._org_id(simulation_id)
        comment = await self.comments.add_comment(
            auth,
            simulation,
            org_id,
            content=body.content,
        )
        author_name, author_email, author_role = await self._author_metadata(
            comment.user_id,
            org_id,
        )
        return _comment_response(
            comment,
            author_name=author_name,
            author_email=author_email,
            author_role=author_role,
        )

    async def submit_review(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
        body: SubmitSimulationReviewRequest,
    ) -> SimulationReviewResponse:
        simulation = await self._require_simulation(auth, simulation_id)
        org_id = await self._org_id(simulation_id)
        review = await self.reviews.submit_review(
            auth,
            simulation,
            org_id,
            status=ReviewStatus(body.status),
            decision_reason=body.decision_reason,
        )
        reviewer_name, reviewer_email, reviewer_role = await self._author_metadata(
            review.reviewer_id,
            org_id,
        )
        return _review_response(
            review,
            reviewer_name=reviewer_name,
            reviewer_email=reviewer_email,
            reviewer_role=reviewer_role,
        )

    async def approve(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
        body: ApproveSimulationRequest,
    ) -> SimulationApprovalResponse:
        simulation = await self._require_simulation(auth, simulation_id)
        org_id = await self._org_id(simulation_id)
        approval = await self.approvals.approve(
            auth,
            simulation,
            org_id,
            stage=ApprovalStage(body.approval_stage),
        )
        return _approval_response(approval)

    async def get_workflow(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
    ) -> SimulationWorkflowResponse:
        simulation = await self._require_simulation(auth, simulation_id)
        org_id = await self._org_id(simulation_id)
        reviews = await self.reviews.list_reviews(simulation_id)
        review_responses = []
        for item in reviews:
            reviewer_name, reviewer_email, reviewer_role = await self._author_metadata(
                item.reviewer_id,
                org_id,
            )
            review_responses.append(
                _review_response(
                    item,
                    reviewer_name=reviewer_name,
                    reviewer_email=reviewer_email,
                    reviewer_role=reviewer_role,
                ),
            )
        approvals = await self.approvals.list_approvals(simulation_id)
        return SimulationWorkflowResponse(
            simulation_id=simulation.id,
            status=simulation.workflow_status.value,
            reviews=review_responses,
            approvals=[_approval_response(item) for item in approvals],
        )

    async def list_activity(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
    ) -> SimulationActivityListResponse:
        await self._require_simulation(auth, simulation_id)
        items = await self.activity.list_for_simulation(simulation_id)
        return SimulationActivityListResponse(
            items=[_activity_response(item) for item in items],
        )

    async def transition_workflow(
        self,
        auth: AuthContext,
        simulation_id: uuid.UUID,
        body: WorkflowTransitionRequest,
    ) -> SimulationWorkflowResponse:
        simulation = await self._require_simulation(auth, simulation_id)
        org_id = await self._org_id(simulation_id)
        await self.workflow.transition(
            auth,
            simulation,
            org_id,
            target=SimulationWorkflowStatus(body.target_status),
        )
        return await self.get_workflow(auth, simulation_id)
