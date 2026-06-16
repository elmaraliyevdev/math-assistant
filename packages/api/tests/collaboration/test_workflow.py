"""Collaboration workflow service tests."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest

from app.auth.context import AuthContext
from app.collaboration.workflow_service import WorkflowService
from app.db.models.organization_member import OrganizationMember, OrganizationRole
from app.db.models.simulation import Simulation
from app.db.models.simulation_workflow import SimulationWorkflowStatus
from app.db.models.user import User


def _auth(role: OrganizationRole, org_id: uuid.UUID) -> AuthContext:
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash="hash",
        full_name="Test User",
    )
    return AuthContext(user=user, memberships={org_id: role})


@pytest.mark.asyncio
async def test_workflow_transition_to_under_review_creates_pending_review() -> None:
    simulation = Simulation(
        id=uuid.uuid4(),
        game_version_id=uuid.uuid4(),
        spin_count=10,
        completed_spin_count=10,
        bet_minor_units=100,
        workflow_status=SimulationWorkflowStatus.DRAFT,
    )
    org_id = uuid.uuid4()
    auth = _auth(OrganizationRole.DEVELOPER, org_id)

    reviews = AsyncMock()
    reviews.add = AsyncMock()
    members = AsyncMock()
    members.list_for_organization.return_value = [
        OrganizationMember(
            organization_id=org_id,
            user_id=uuid.uuid4(),
            role=OrganizationRole.ADMIN,
        ),
    ]
    activity = AsyncMock()
    activity.record = AsyncMock()
    notifications = AsyncMock()
    notifications.create_collaboration_notification = AsyncMock()

    service = WorkflowService(reviews, members, activity, notifications)
    updated = await service.transition(
        auth,
        simulation,
        org_id,
        target=SimulationWorkflowStatus.UNDER_REVIEW,
    )

    assert updated.workflow_status == SimulationWorkflowStatus.UNDER_REVIEW
    reviews.add.assert_awaited_once()
    activity.record.assert_awaited()
    notifications.create_collaboration_notification.assert_awaited()


@pytest.mark.asyncio
async def test_invalid_transition_raises() -> None:
    from app.exceptions.domain import InvalidWorkflowTransitionError

    simulation = Simulation(
        id=uuid.uuid4(),
        game_version_id=uuid.uuid4(),
        spin_count=10,
        completed_spin_count=10,
        bet_minor_units=100,
        workflow_status=SimulationWorkflowStatus.DRAFT,
    )
    org_id = uuid.uuid4()
    auth = _auth(OrganizationRole.VIEWER, org_id)
    service = WorkflowService(AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock())

@pytest.mark.asyncio
async def test_workflow_certification_ready_notification() -> None:
    simulation = Simulation(
        id=uuid.uuid4(),
        game_version_id=uuid.uuid4(),
        spin_count=10,
        completed_spin_count=10,
        bet_minor_units=100,
        workflow_status=SimulationWorkflowStatus.APPROVED,
        created_by_user_id=uuid.uuid4(),
    )
    org_id = uuid.uuid4()
    auth = _auth(OrganizationRole.ADMIN, org_id)
    activity = AsyncMock()
    activity.record = AsyncMock()
    notifications = AsyncMock()
    notifications.create_collaboration_notification = AsyncMock()
    service = WorkflowService(AsyncMock(), AsyncMock(), activity, notifications)

    updated = await service.transition(
        auth,
        simulation,
        org_id,
        target=SimulationWorkflowStatus.CERTIFICATION_READY,
    )
    assert updated.workflow_status == SimulationWorkflowStatus.CERTIFICATION_READY
    notifications.create_collaboration_notification.assert_awaited()


def test_workflow_service_get_status() -> None:
    simulation = Simulation(
        id=uuid.uuid4(),
        game_version_id=uuid.uuid4(),
        spin_count=1,
        completed_spin_count=1,
        bet_minor_units=100,
        workflow_status=SimulationWorkflowStatus.DRAFT,
    )
    service = WorkflowService(AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock())
    assert service.get_status(simulation) == SimulationWorkflowStatus.DRAFT


@pytest.mark.asyncio
async def test_invalid_transition_raises() -> None:
    from app.exceptions.domain import InvalidWorkflowTransitionError

    simulation = Simulation(
        id=uuid.uuid4(),
        game_version_id=uuid.uuid4(),
        spin_count=10,
        completed_spin_count=10,
        bet_minor_units=100,
        workflow_status=SimulationWorkflowStatus.DRAFT,
    )
    org_id = uuid.uuid4()
    auth = _auth(OrganizationRole.VIEWER, org_id)
    service = WorkflowService(AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock())

    with pytest.raises(InvalidWorkflowTransitionError):
        await service.transition(
            auth,
            simulation,
            org_id,
            target=SimulationWorkflowStatus.RELEASED,
        )
