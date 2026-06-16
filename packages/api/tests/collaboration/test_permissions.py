"""Collaboration permission tests."""

from __future__ import annotations

from app.collaboration.permissions import (
    ALLOWED_TRANSITIONS,
    can_approve_stage,
    can_comment,
    can_request_review,
    can_transition,
)
from app.db.models.organization_member import OrganizationRole
from app.db.models.simulation_workflow import ApprovalStage, SimulationWorkflowStatus


def test_viewer_cannot_approve_any_stage() -> None:
    for stage in ApprovalStage:
        assert not can_approve_stage(OrganizationRole.VIEWER, stage)


def test_permissions_return_false_for_unknown_paths() -> None:
    assert not can_transition(
        OrganizationRole.ADMIN,
        SimulationWorkflowStatus.RELEASED,
        SimulationWorkflowStatus.DRAFT,
    )
    assert ALLOWED_TRANSITIONS[SimulationWorkflowStatus.RELEASED] == set()


def test_developer_can_comment_and_request_review() -> None:
    assert can_comment(OrganizationRole.DEVELOPER)
    assert can_request_review(OrganizationRole.DEVELOPER)
    assert not can_comment(OrganizationRole.VIEWER)


def test_approval_stage_permissions() -> None:
    assert can_approve_stage(OrganizationRole.ADMIN, ApprovalStage.MATHEMATICIAN)
    assert can_approve_stage(OrganizationRole.OWNER, ApprovalStage.PRODUCER)
    assert not can_approve_stage(OrganizationRole.DEVELOPER, ApprovalStage.MATHEMATICIAN)
    assert not can_approve_stage(OrganizationRole.ADMIN, ApprovalStage.PRODUCER)


def test_workflow_transitions() -> None:
    assert SimulationWorkflowStatus.UNDER_REVIEW in ALLOWED_TRANSITIONS[
        SimulationWorkflowStatus.DRAFT
    ]
    assert can_transition(
        OrganizationRole.DEVELOPER,
        SimulationWorkflowStatus.DRAFT,
        SimulationWorkflowStatus.UNDER_REVIEW,
    )
    assert not can_transition(
        OrganizationRole.VIEWER,
        SimulationWorkflowStatus.DRAFT,
        SimulationWorkflowStatus.UNDER_REVIEW,
    )
    assert can_transition(
        OrganizationRole.OWNER,
        SimulationWorkflowStatus.CERTIFICATION_READY,
        SimulationWorkflowStatus.RELEASED,
    )
    assert not can_transition(
        OrganizationRole.ADMIN,
        SimulationWorkflowStatus.CERTIFICATION_READY,
        SimulationWorkflowStatus.RELEASED,
    )
