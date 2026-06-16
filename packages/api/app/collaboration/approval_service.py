"""Simulation stage approval service."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.auth.context import AuthContext
from app.collaboration.activity_service import ActivityService
from app.collaboration.permissions import can_approve_stage
from app.db.models.organization_member import OrganizationRole
from app.db.models.simulation import Simulation
from app.db.models.simulation_approval import SimulationApproval
from app.db.models.simulation_workflow import ApprovalStage
from app.db.repositories.simulation_approval_repository import SimulationApprovalRepository
from app.exceptions.domain import DuplicateApprovalError, ForbiddenError


class ApprovalService:
    def __init__(
        self,
        approvals: SimulationApprovalRepository,
        activity: ActivityService,
    ) -> None:
        self._approvals = approvals
        self._activity = activity

    async def list_approvals(self, simulation_id: uuid.UUID) -> list[SimulationApproval]:
        return await self._approvals.list_by_simulation_id(simulation_id)

    async def approve(
        self,
        auth: AuthContext,
        simulation: Simulation,
        org_id: uuid.UUID,
        *,
        stage: ApprovalStage,
    ) -> SimulationApproval:
        role = auth.memberships.get(org_id, OrganizationRole.VIEWER)
        if not can_approve_stage(role, stage):
            raise ForbiddenError(
                message=f"insufficient permissions to approve at stage {stage.value}",
            )

        existing = await self._approvals.get_by_stage(simulation.id, stage)
        if existing is not None:
            raise DuplicateApprovalError(
                simulation_id=str(simulation.id),
                stage=stage.value,
            )

        approval = SimulationApproval(
            simulation_id=simulation.id,
            approved_by=auth.user_id,
            approval_stage=stage,
            approved_at=datetime.now(UTC),
        )
        await self._approvals.add(approval)
        await self._activity.record(
            simulation_id=simulation.id,
            actor_id=auth.user_id,
            action="stage_approved",
            metadata={"stage": stage.value, "approvalId": str(approval.id)},
        )
        return approval
