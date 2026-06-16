"""Organization service unit tests."""

from __future__ import annotations

import uuid

import pytest

from app.db.models.organization import Organization
from app.db.models.organization_member import OrganizationRole
from app.db.models.user import User
from app.exceptions.domain import (
    DuplicateOrganizationSlugError,
    ForbiddenError,
    MemberNotFoundError,
    OrganizationAccessDeniedError,
    UserNotFoundError,
)
from app.schemas.organizations import (
    AddOrganizationMemberRequest,
    CreateOrganizationRequest,
    UpdateOrganizationRequest,
)
from app.security.passwords import hash_password
from app.services.organization_service import OrganizationService


@pytest.mark.asyncio
async def test_create_and_list_organizations(
    db_session,
    auth_context,
) -> None:
    service = OrganizationService.from_session(db_session)
    created = await service.create_organization(
        auth_context,
        CreateOrganizationRequest(name="Studio", slug="studio"),
    )
    assert created.slug == "studio"

    listed = await service.list_organizations(auth_context)
    assert len(listed.items) >= 1


@pytest.mark.asyncio
async def test_create_organization_duplicate_slug(
    db_session,
    auth_context,
    organization_repo,
    sample_organization,
) -> None:
    await organization_repo.add(sample_organization)
    service = OrganizationService.from_session(db_session)
    with pytest.raises(DuplicateOrganizationSlugError):
        await service.create_organization(
            auth_context,
            CreateOrganizationRequest(
                name="Duplicate",
                slug=sample_organization.slug,
            ),
        )


@pytest.mark.asyncio
async def test_get_organization_access_denied(
    db_session,
    auth_context,
    organization_repo,
) -> None:
    other_org = await organization_repo.add(
        Organization(name="Other", slug="other-org"),
    )
    service = OrganizationService.from_session(db_session)
    with pytest.raises(OrganizationAccessDeniedError):
        await service.get_organization(auth_context, other_org.id)


@pytest.mark.asyncio
async def test_update_organization_as_owner(
    db_session,
    auth_context,
) -> None:
    service = OrganizationService.from_session(db_session)
    org_id = auth_context.organization_ids[0]
    updated = await service.update_organization(
        auth_context,
        org_id,
        UpdateOrganizationRequest(name="Updated Name"),
    )
    assert updated.name == "Updated Name"


@pytest.mark.asyncio
async def test_add_member_and_remove_member(
    db_session,
    auth_context,
    user_repo,
) -> None:
    other_user = await user_repo.add(
        User(
            email="member@example.com",
            password_hash=hash_password("secure-password"),
            full_name="Member User",
            is_active=True,
        ),
    )
    service = OrganizationService.from_session(db_session)
    org_id = auth_context.organization_ids[0]

    added = await service.add_member(
        auth_context,
        org_id,
        AddOrganizationMemberRequest(
            user_id=other_user.id,
            role=OrganizationRole.DEVELOPER,
        ),
    )
    assert added.role == OrganizationRole.DEVELOPER.value

    await service.remove_member(auth_context, org_id, other_user.id)


@pytest.mark.asyncio
async def test_add_member_user_not_found(
    db_session,
    auth_context,
) -> None:
    service = OrganizationService.from_session(db_session)
    with pytest.raises(UserNotFoundError):
        await service.add_member(
            auth_context,
            auth_context.organization_ids[0],
            AddOrganizationMemberRequest(
                user_id=uuid.uuid4(),
                role=OrganizationRole.VIEWER,
            ),
        )


@pytest.mark.asyncio
async def test_add_owner_role_forbidden(
    db_session,
    auth_context,
    user_repo,
) -> None:
    other_user = await user_repo.add(
        User(
            email="owner-target@example.com",
            password_hash=hash_password("secure-password"),
            full_name="Owner Target",
            is_active=True,
        ),
    )
    service = OrganizationService.from_session(db_session)
    with pytest.raises(ForbiddenError):
        await service.add_member(
            auth_context,
            auth_context.organization_ids[0],
            AddOrganizationMemberRequest(
                user_id=other_user.id,
                role=OrganizationRole.OWNER,
            ),
        )


@pytest.mark.asyncio
async def test_remove_member_not_found(
    db_session,
    auth_context,
) -> None:
    service = OrganizationService.from_session(db_session)
    with pytest.raises(MemberNotFoundError):
        await service.remove_member(
            auth_context,
            auth_context.organization_ids[0],
            uuid.uuid4(),
        )


@pytest.mark.asyncio
async def test_remove_owner_forbidden(
    db_session,
    auth_context,
) -> None:
    service = OrganizationService.from_session(db_session)
    with pytest.raises(ForbiddenError):
        await service.remove_member(
            auth_context,
            auth_context.organization_ids[0],
            auth_context.user.id,
        )
