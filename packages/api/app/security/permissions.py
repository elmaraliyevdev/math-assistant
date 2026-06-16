"""Organization role permission checks."""

from __future__ import annotations

from app.db.models.organization_member import OrganizationRole

ROLE_RANK: dict[OrganizationRole, int] = {
    OrganizationRole.VIEWER: 1,
    OrganizationRole.DEVELOPER: 2,
    OrganizationRole.ADMIN: 3,
    OrganizationRole.OWNER: 4,
}


def role_at_least(role: OrganizationRole, minimum: OrganizationRole) -> bool:
    return ROLE_RANK[role] >= ROLE_RANK[minimum]


def can_read(role: OrganizationRole) -> bool:
    return role_at_least(role, OrganizationRole.VIEWER)


def can_write_games(role: OrganizationRole) -> bool:
    return role_at_least(role, OrganizationRole.DEVELOPER)


def can_manage_members(role: OrganizationRole) -> bool:
    return role_at_least(role, OrganizationRole.ADMIN)


def can_manage_organization(role: OrganizationRole) -> bool:
    return role_at_least(role, OrganizationRole.OWNER)
