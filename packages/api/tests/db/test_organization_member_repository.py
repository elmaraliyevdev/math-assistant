"""Organization member repository tests."""

from __future__ import annotations

import uuid

import pytest

from app.db.models.organization_member import OrganizationMember, OrganizationRole


@pytest.mark.asyncio
async def test_member_repository_crud(
    organization_repo,
    user_repo,
    organization_member_repo,
    sample_organization,
    sample_user,
) -> None:
    organization = await organization_repo.add(sample_organization)
    user = await user_repo.add(sample_user)

    membership = await organization_member_repo.add_member(
        organization_id=organization.id,
        user_id=user.id,
        role=OrganizationRole.DEVELOPER,
    )
    assert membership.role == OrganizationRole.DEVELOPER

    fetched = await organization_member_repo.get_membership(
        organization_id=organization.id,
        user_id=user.id,
    )
    assert fetched is not None

    user_memberships = await organization_member_repo.list_for_user(user.id)
    assert len(user_memberships) == 1

    org_members = await organization_member_repo.list_for_organization(organization.id)
    assert len(org_members) == 1

    membership.role = OrganizationRole.ADMIN
    await organization_member_repo.save(membership)

    await organization_member_repo.delete_membership(
        organization_id=organization.id,
        user_id=user.id,
    )
    assert await organization_member_repo.get_membership(
        organization_id=organization.id,
        user_id=user.id,
    ) is None


@pytest.mark.asyncio
async def test_delete_missing_membership_is_noop(
    organization_member_repo,
) -> None:
    await organization_member_repo.delete_membership(
        organization_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
    )
