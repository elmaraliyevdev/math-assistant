"""Collaboration facade and edge-case tests."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.auth.context import AuthContext
from app.collaboration.permissions import can_transition
from app.collaboration.service import CollaborationService, _activity_response
from app.db.models.organization_member import OrganizationRole
from app.db.models.simulation_workflow import ApprovalStage, SimulationWorkflowStatus
from app.db.models.user import User
from app.exceptions.domain import SimulationNotFoundError
from app.schemas.collaboration import (
    ApproveSimulationRequest,
    CreateSimulationCommentRequest,
    SubmitSimulationReviewRequest,
    WorkflowTransitionRequest,
)


def _auth(role: OrganizationRole, org_id: uuid.UUID) -> AuthContext:
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash="hash",
        full_name="Test User",
    )
    return AuthContext(user=user, memberships={org_id: role})


def _simulation(org_id: uuid.UUID | None = None):
    simulation = MagicMock()
    simulation.id = uuid.uuid4()
    simulation.game_version_id = uuid.uuid4()
    simulation.workflow_status = SimulationWorkflowStatus.DRAFT
    simulation.created_by_user_id = uuid.uuid4()
    return simulation


@pytest.mark.asyncio
async def test_collaboration_service_facade_paths() -> None:
    org_id = uuid.uuid4()
    auth = _auth(OrganizationRole.OWNER, org_id)
    simulation = _simulation()
    simulation.workflow_status = SimulationWorkflowStatus.UNDER_REVIEW

    simulations = AsyncMock()
    simulations.get_by_id_for_organizations.return_value = simulation
    simulations.get_organization_id.return_value = org_id

    comments = AsyncMock()
    comment = MagicMock()
    comment.id = uuid.uuid4()
    comment.simulation_id = simulation.id
    comment.user_id = auth.user_id
    comment.content = "hello"
    comment.created_at = MagicMock()
    comments.add_comment.return_value = comment
    comments.list_comments.return_value = [comment]

    reviews = AsyncMock()
    review = MagicMock()
    review.id = uuid.uuid4()
    review.simulation_id = simulation.id
    review.reviewer_id = auth.user_id
    review.status = MagicMock(value="approved")
    review.decision_reason = None
    review.created_at = MagicMock()
    review.updated_at = MagicMock()
    reviews.submit_review.return_value = review
    reviews.list_reviews.return_value = [review]

    approvals = AsyncMock()
    approval = MagicMock()
    approval.id = uuid.uuid4()
    approval.simulation_id = simulation.id
    approval.approved_by = auth.user_id
    approval.approval_stage = MagicMock(value="mathematician")
    approval.approved_at = MagicMock()
    approvals.approve.return_value = approval
    approvals.list_approvals.return_value = [approval]

    workflow = AsyncMock()
    workflow.transition.return_value = simulation

    activity = AsyncMock()
    log = MagicMock()
    log.id = uuid.uuid4()
    log.simulation_id = simulation.id
    log.actor_id = auth.user_id
    log.action = "comment_added"
    log.metadata_json = {"commentId": "1"}
    log.created_at = MagicMock()
    activity.list_for_simulation.return_value = [log]

    users = AsyncMock()
    user = User(
        id=auth.user_id,
        email="test@example.com",
        password_hash="hash",
        full_name="Test User",
    )
    users.get_by_id.return_value = user

    members = AsyncMock()
    membership = MagicMock()
    membership.role = OrganizationRole.OWNER
    members.get_membership.return_value = membership

    service = CollaborationService(
        simulations=simulations,
        comments=comments,
        reviews=reviews,
        approvals=approvals,
        workflow=workflow,
        activity=activity,
        users=users,
        members=members,
    )
    sim_id = simulation.id

    listed = await service.list_comments(auth, sim_id)
    assert len(listed.items) == 1

    created = await service.add_comment(
        auth,
        sim_id,
        CreateSimulationCommentRequest(content="hello"),
    )
    assert created.content == "hello"

    submitted = await service.submit_review(
        auth,
        sim_id,
        SubmitSimulationReviewRequest(status="approved"),
    )
    assert submitted.status == "approved"

    approved = await service.approve(
        auth,
        sim_id,
        ApproveSimulationRequest(approval_stage="mathematician"),
    )
    assert approved.approval_stage == "mathematician"

    workflow_state = await service.get_workflow(auth, sim_id)
    assert workflow_state.status == SimulationWorkflowStatus.UNDER_REVIEW.value

    activity_list = await service.list_activity(auth, sim_id)
    assert len(activity_list.items) == 1
    assert _activity_response(log).action == "comment_added"

    transitioned = await service.transition_workflow(
        auth,
        sim_id,
        WorkflowTransitionRequest(target_status="approved"),
    )
    assert transitioned.simulation_id == sim_id
    workflow.transition.assert_awaited()


@pytest.mark.asyncio
async def test_collaboration_service_simulation_not_found() -> None:
    org_id = uuid.uuid4()
    auth = _auth(OrganizationRole.OWNER, org_id)
    simulations = AsyncMock()
    simulations.get_by_id_for_organizations.return_value = None
    service = CollaborationService(
        simulations=simulations,
        comments=AsyncMock(),
        reviews=AsyncMock(),
        approvals=AsyncMock(),
        workflow=AsyncMock(),
        activity=AsyncMock(),
        users=AsyncMock(),
        members=AsyncMock(),
    )

    with pytest.raises(SimulationNotFoundError):
        await service.list_comments(auth, uuid.uuid4())


def test_permissions_additional_branches() -> None:
    assert not can_transition(
        OrganizationRole.DEVELOPER,
        SimulationWorkflowStatus.UNDER_REVIEW,
        SimulationWorkflowStatus.APPROVED,
    )
    assert can_transition(
        OrganizationRole.ADMIN,
        SimulationWorkflowStatus.UNDER_REVIEW,
        SimulationWorkflowStatus.DRAFT,
    )
    assert not can_transition(
        OrganizationRole.DEVELOPER,
        SimulationWorkflowStatus.APPROVED,
        SimulationWorkflowStatus.CERTIFICATION_READY,
    )
