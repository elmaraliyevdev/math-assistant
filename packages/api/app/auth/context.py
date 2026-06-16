"""Authenticated request context."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.db.models.organization_member import OrganizationRole
from app.db.models.user import User
from app.exceptions.domain import ForbiddenError, OrganizationAccessDeniedError
from app.security.permissions import role_at_least


@dataclass(frozen=True, slots=True)
class AuthContext:
    user: User
    memberships: dict[uuid.UUID, OrganizationRole]

    @property
    def user_id(self) -> uuid.UUID:
        return self.user.id

    @property
    def organization_ids(self) -> list[uuid.UUID]:
        return list(self.memberships.keys())

    def role_in(self, organization_id: uuid.UUID) -> OrganizationRole | None:
        return self.memberships.get(organization_id)

    def require_membership(self, organization_id: uuid.UUID) -> OrganizationRole:
        role = self.role_in(organization_id)
        if role is None:
            raise OrganizationAccessDeniedError(organization_id=str(organization_id))
        return role

    def require_role(
        self,
        organization_id: uuid.UUID,
        minimum_role: OrganizationRole,
    ) -> OrganizationRole:
        role = self.require_membership(organization_id)
        if not role_at_least(role, minimum_role):
            raise ForbiddenError(
                message="insufficient permissions for this organization",
                details={
                    "organizationId": str(organization_id),
                    "requiredRole": minimum_role.value,
                    "actualRole": role.value,
                },
            )
        return role
