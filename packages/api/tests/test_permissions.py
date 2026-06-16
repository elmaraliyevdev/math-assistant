"""Permission helper tests."""

from __future__ import annotations

from app.db.models.organization_member import OrganizationRole
from app.security.permissions import (
    can_manage_members,
    can_manage_organization,
    can_read,
    can_write_games,
    role_at_least,
)


def test_role_at_least() -> None:
    assert role_at_least(OrganizationRole.OWNER, OrganizationRole.DEVELOPER)
    assert not role_at_least(OrganizationRole.VIEWER, OrganizationRole.DEVELOPER)


def test_permission_helpers() -> None:
    assert can_read(OrganizationRole.VIEWER)
    assert can_write_games(OrganizationRole.DEVELOPER)
    assert can_manage_members(OrganizationRole.ADMIN)
    assert can_manage_organization(OrganizationRole.OWNER)
    assert not can_manage_organization(OrganizationRole.ADMIN)
