"""Collaboration workflow permissions."""

from __future__ import annotations

from app.db.models.organization_member import OrganizationRole
from app.db.models.simulation_workflow import ApprovalStage, SimulationWorkflowStatus
from app.security.permissions import role_at_least


def can_comment(role: OrganizationRole) -> bool:
    return role_at_least(role, OrganizationRole.DEVELOPER)


def can_request_review(role: OrganizationRole) -> bool:
    return role_at_least(role, OrganizationRole.DEVELOPER)


def can_approve_stage(role: OrganizationRole, stage: ApprovalStage) -> bool:
    if stage == ApprovalStage.MATHEMATICIAN:
        return role_at_least(role, OrganizationRole.ADMIN)
    if stage == ApprovalStage.SENIOR_MATHEMATICIAN:
        return role_at_least(role, OrganizationRole.ADMIN)
    if stage == ApprovalStage.PRODUCT_OWNER:
        return role_at_least(role, OrganizationRole.ADMIN)
    if stage == ApprovalStage.PRODUCER:
        return role_at_least(role, OrganizationRole.OWNER)
    return False


ALLOWED_TRANSITIONS: dict[SimulationWorkflowStatus, set[SimulationWorkflowStatus]] = {
    SimulationWorkflowStatus.DRAFT: {SimulationWorkflowStatus.UNDER_REVIEW},
    SimulationWorkflowStatus.UNDER_REVIEW: {
        SimulationWorkflowStatus.APPROVED,
        SimulationWorkflowStatus.DRAFT,
    },
    SimulationWorkflowStatus.APPROVED: {SimulationWorkflowStatus.CERTIFICATION_READY},
    SimulationWorkflowStatus.CERTIFICATION_READY: {SimulationWorkflowStatus.RELEASED},
    SimulationWorkflowStatus.RELEASED: set(),
}


def can_transition(
    role: OrganizationRole,
    current: SimulationWorkflowStatus,
    target: SimulationWorkflowStatus,
) -> bool:
    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        return False
    if current == SimulationWorkflowStatus.DRAFT and target == SimulationWorkflowStatus.UNDER_REVIEW:
        return can_request_review(role)
    if current == SimulationWorkflowStatus.UNDER_REVIEW and target == SimulationWorkflowStatus.DRAFT:
        return role_at_least(role, OrganizationRole.ADMIN)
    if current == SimulationWorkflowStatus.UNDER_REVIEW and target == SimulationWorkflowStatus.APPROVED:
        return role_at_least(role, OrganizationRole.ADMIN)
    if current == SimulationWorkflowStatus.APPROVED and target == SimulationWorkflowStatus.CERTIFICATION_READY:
        return role_at_least(role, OrganizationRole.ADMIN)
    if current == SimulationWorkflowStatus.CERTIFICATION_READY and target == SimulationWorkflowStatus.RELEASED:
        return role_at_least(role, OrganizationRole.OWNER)
    return False
