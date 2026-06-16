"""Simulation collaboration comments service."""

from __future__ import annotations

import uuid

from app.auth.context import AuthContext
from app.collaboration.activity_service import ActivityService
from app.collaboration.permissions import can_comment
from app.db.models.organization_member import OrganizationRole
from app.db.models.simulation import Simulation
from app.db.models.simulation_comment import SimulationComment
from app.db.repositories.simulation_comment_repository import SimulationCommentRepository
from app.exceptions.domain import ForbiddenError


class CommentsService:
    def __init__(
        self,
        repository: SimulationCommentRepository,
        activity: ActivityService,
    ) -> None:
        self._repository = repository
        self._activity = activity

    async def list_comments(self, simulation_id: uuid.UUID) -> list[SimulationComment]:
        return await self._repository.list_by_simulation_id(simulation_id)

    async def add_comment(
        self,
        auth: AuthContext,
        simulation: Simulation,
        org_id: uuid.UUID,
        *,
        content: str,
    ) -> SimulationComment:
        role = auth.memberships.get(org_id, OrganizationRole.VIEWER)
        if not can_comment(role):
            raise ForbiddenError(message="insufficient permissions to comment")
        comment = SimulationComment(
            simulation_id=simulation.id,
            user_id=auth.user_id,
            content=content.strip(),
        )
        await self._repository.add(comment)
        await self._activity.record(
            simulation_id=simulation.id,
            actor_id=auth.user_id,
            action="comment_added",
            metadata={"commentId": str(comment.id)},
        )
        return comment
