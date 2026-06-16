"""Collaboration service unit tests."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest

from app.auth.context import AuthContext
from app.collaboration.activity_service import ActivityService
from app.collaboration.approval_service import ApprovalService
from app.collaboration.comments_service import CommentsService
from app.collaboration.review_service import ReviewService
from app.db.models.organization_member import OrganizationRole
from app.db.models.simulation import Simulation
from app.db.models.simulation_workflow import ApprovalStage, ReviewStatus, SimulationWorkflowStatus
from app.db.models.user import User
from app.exceptions.domain import DuplicateApprovalError, ForbiddenError


def _auth(role: OrganizationRole, org_id: uuid.UUID) -> AuthContext:
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash="hash",
        full_name="Test User",
    )
    return AuthContext(user=user, memberships={org_id: role})


@pytest.mark.asyncio
async def test_comments_service_records_activity() -> None:
    simulation = Simulation(
        id=uuid.uuid4(),
        game_version_id=uuid.uuid4(),
        spin_count=1,
        completed_spin_count=1,
        bet_minor_units=100,
    )
    org_id = uuid.uuid4()
    auth = _auth(OrganizationRole.DEVELOPER, org_id)
    repository = AsyncMock()
    repository.add = AsyncMock(side_effect=lambda entity: entity)
    activity = AsyncMock()
    activity.record = AsyncMock()
    service = CommentsService(repository, activity)

    comment = await service.add_comment(auth, simulation, org_id, content="note")
    assert comment.content == "note"
    activity.record.assert_awaited_once()


@pytest.mark.asyncio
async def test_comments_forbidden_for_viewer() -> None:
    simulation = Simulation(
        id=uuid.uuid4(),
        game_version_id=uuid.uuid4(),
        spin_count=1,
        completed_spin_count=1,
        bet_minor_units=100,
    )
    org_id = uuid.uuid4()
    auth = _auth(OrganizationRole.VIEWER, org_id)
    service = CommentsService(AsyncMock(), AsyncMock())

    with pytest.raises(ForbiddenError):
        await service.add_comment(auth, simulation, org_id, content="nope")


@pytest.mark.asyncio
async def test_approval_service_duplicate_stage() -> None:
    simulation = Simulation(
        id=uuid.uuid4(),
        game_version_id=uuid.uuid4(),
        spin_count=1,
        completed_spin_count=1,
        bet_minor_units=100,
    )
    org_id = uuid.uuid4()
    auth = _auth(OrganizationRole.ADMIN, org_id)
    approvals = AsyncMock()
    approvals.get_by_stage.return_value = object()
    service = ApprovalService(approvals, AsyncMock())

    with pytest.raises(DuplicateApprovalError):
        await service.approve(
            auth,
            simulation,
            org_id,
            stage=ApprovalStage.MATHEMATICIAN,
        )


@pytest.mark.asyncio
async def test_review_service_changes_requested_sets_draft() -> None:
    simulation = Simulation(
        id=uuid.uuid4(),
        game_version_id=uuid.uuid4(),
        spin_count=1,
        completed_spin_count=1,
        bet_minor_units=100,
        workflow_status=SimulationWorkflowStatus.UNDER_REVIEW,
        created_by_user_id=uuid.uuid4(),
    )
    org_id = uuid.uuid4()
    auth = _auth(OrganizationRole.ADMIN, org_id)
    reviews = AsyncMock()
    reviews.add = AsyncMock(side_effect=lambda entity: entity)
    activity = AsyncMock()
    activity.record = AsyncMock()
    notifications = AsyncMock()
    notifications.create_collaboration_notification = AsyncMock()
    service = ReviewService(reviews, AsyncMock(), activity, notifications)

    await service.submit_review(
        auth,
        simulation,
        org_id,
        status=ReviewStatus.CHANGES_REQUESTED,
        decision_reason="fix rtp",
    )
    assert simulation.workflow_status == SimulationWorkflowStatus.DRAFT


@pytest.mark.asyncio
async def test_review_service_requires_decision_reason() -> None:
    simulation = Simulation(
        id=uuid.uuid4(),
        game_version_id=uuid.uuid4(),
        spin_count=1,
        completed_spin_count=1,
        bet_minor_units=100,
        workflow_status=SimulationWorkflowStatus.UNDER_REVIEW,
    )
    org_id = uuid.uuid4()
    auth = _auth(OrganizationRole.ADMIN, org_id)
    service = ReviewService(AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock())

    from app.exceptions.domain import ReviewDecisionRequiredError

    with pytest.raises(ReviewDecisionRequiredError):
        await service.submit_review(
            auth,
            simulation,
            org_id,
            status=ReviewStatus.REJECTED,
            decision_reason="",
        )


@pytest.mark.asyncio
async def test_review_service_rejected_and_forbidden() -> None:
    simulation = Simulation(
        id=uuid.uuid4(),
        game_version_id=uuid.uuid4(),
        spin_count=1,
        completed_spin_count=1,
        bet_minor_units=100,
        workflow_status=SimulationWorkflowStatus.UNDER_REVIEW,
    )
    org_id = uuid.uuid4()
    auth = _auth(OrganizationRole.DEVELOPER, org_id)
    service = ReviewService(AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock())

    with pytest.raises(ForbiddenError):
        await service.submit_review(
            auth,
            simulation,
            org_id,
            status=ReviewStatus.APPROVED,
            decision_reason=None,
        )

    admin = _auth(OrganizationRole.ADMIN, org_id)
    reviews = AsyncMock()
    reviews.add = AsyncMock(side_effect=lambda entity: entity)
    activity = AsyncMock()
    activity.record = AsyncMock()
    notifications = AsyncMock()
    notifications.create_collaboration_notification = AsyncMock()
    service = ReviewService(reviews, AsyncMock(), activity, notifications)

    await service.submit_review(
        admin,
        simulation,
        org_id,
        status=ReviewStatus.REJECTED,
        decision_reason="not good",
    )
    assert simulation.workflow_status == SimulationWorkflowStatus.DRAFT


@pytest.mark.asyncio
async def test_approval_service_forbidden_and_success() -> None:
    simulation = Simulation(
        id=uuid.uuid4(),
        game_version_id=uuid.uuid4(),
        spin_count=1,
        completed_spin_count=1,
        bet_minor_units=100,
    )
    org_id = uuid.uuid4()
    auth = _auth(OrganizationRole.DEVELOPER, org_id)
    service = ApprovalService(AsyncMock(), AsyncMock())

    with pytest.raises(ForbiddenError):
        await service.approve(
            auth,
            simulation,
            org_id,
            stage=ApprovalStage.MATHEMATICIAN,
        )

    admin = _auth(OrganizationRole.ADMIN, org_id)
    approvals = AsyncMock()
    approvals.get_by_stage.return_value = None
    approvals.add = AsyncMock(side_effect=lambda entity: entity)
    activity = AsyncMock()
    activity.record = AsyncMock()
    service = ApprovalService(approvals, activity)

    result = await service.approve(
        admin,
        simulation,
        org_id,
        stage=ApprovalStage.PRODUCT_OWNER,
    )
    assert result.approval_stage == ApprovalStage.PRODUCT_OWNER


@pytest.mark.asyncio
async def test_activity_service_record() -> None:
    repository = AsyncMock()
    repository.add = AsyncMock(side_effect=lambda entity: entity)
    service = ActivityService(repository)
    sim_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    entry = await service.record(
        simulation_id=sim_id,
        actor_id=actor_id,
        action="workflow_transition",
        metadata={"to": "approved"},
    )
    assert entry.action == "workflow_transition"
    repository.add.assert_awaited_once()


@pytest.mark.asyncio
async def test_review_service_approved_notifies() -> None:
    simulation = Simulation(
        id=uuid.uuid4(),
        game_version_id=uuid.uuid4(),
        spin_count=1,
        completed_spin_count=1,
        bet_minor_units=100,
        workflow_status=SimulationWorkflowStatus.UNDER_REVIEW,
        created_by_user_id=uuid.uuid4(),
    )
    org_id = uuid.uuid4()
    admin = _auth(OrganizationRole.ADMIN, org_id)
    reviews = AsyncMock()
    reviews.add = AsyncMock(side_effect=lambda entity: entity)
    activity = AsyncMock()
    notifications = AsyncMock()
    notifications.create_collaboration_notification = AsyncMock()
    service = ReviewService(reviews, AsyncMock(), activity, notifications)

    await service.submit_review(
        admin,
        simulation,
        org_id,
        status=ReviewStatus.APPROVED,
        decision_reason=None,
    )
    assert simulation.workflow_status == SimulationWorkflowStatus.APPROVED
    notifications.create_collaboration_notification.assert_awaited()
