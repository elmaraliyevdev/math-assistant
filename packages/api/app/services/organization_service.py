"""Organization management service."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import AuthContext
from app.db.models.organization import Organization
from app.db.models.organization_member import OrganizationRole
from app.db.repositories.organization_member_repository import OrganizationMemberRepository
from app.db.repositories.organization_repository import OrganizationRepository
from app.db.repositories.user_repository import UserRepository
from app.exceptions.domain import (
    DuplicateOrganizationSlugError,
    ForbiddenError,
    MemberNotFoundError,
    OrganizationNotFoundError,
    UserNotFoundError,
)
from app.schemas.organizations import (
    AddOrganizationMemberRequest,
    CreateOrganizationRequest,
    OrganizationListResponse,
    OrganizationMemberListResponse,
    OrganizationMemberResponse,
    OrganizationResponse,
    TransferOwnershipRequest,
    UpdateOrganizationRequest,
)
from app.db.models.notification import NotificationType
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService
from app.security.permissions import can_manage_members, can_manage_organization


def _to_member_response(membership) -> OrganizationMemberResponse:
    user = membership.user
    return OrganizationMemberResponse(
        user_id=membership.user_id,
        organization_id=membership.organization_id,
        role=membership.role.value,
        email=user.email if user is not None else None,
        full_name=user.full_name if user is not None else None,
    )


def _to_organization_response(organization: Organization) -> OrganizationResponse:
    return OrganizationResponse(
        id=organization.id,
        name=organization.name,
        slug=organization.slug,
        created_at=organization.created_at,
        updated_at=organization.updated_at,
    )


@dataclass(frozen=True, slots=True)
class OrganizationService:
    organizations: OrganizationRepository
    members: OrganizationMemberRepository
    users: UserRepository

    @classmethod
    def from_session(cls, session: AsyncSession) -> OrganizationService:
        return cls(
            organizations=OrganizationRepository(session),
            members=OrganizationMemberRepository(session),
            users=UserRepository(session),
        )

    async def create_organization(
        self,
        auth: AuthContext,
        body: CreateOrganizationRequest,
    ) -> OrganizationResponse:
        if await self.organizations.get_by_slug(body.slug) is not None:
            raise DuplicateOrganizationSlugError(slug=body.slug)

        organization = Organization(name=body.name, slug=body.slug)
        created = await self.organizations.add(organization)
        await self.members.add_member(
            organization_id=created.id,
            user_id=auth.user.id,
            role=OrganizationRole.OWNER,
        )
        return _to_organization_response(created)

    async def list_organizations(self, auth: AuthContext) -> OrganizationListResponse:
        organizations = await self.organizations.list_for_user(auth.user.id)
        return OrganizationListResponse(
            items=[_to_organization_response(org) for org in organizations],
        )

    async def get_organization(
        self,
        auth: AuthContext,
        organization_id: uuid.UUID,
    ) -> OrganizationResponse:
        auth.require_membership(organization_id)
        organization = await self._require_organization(organization_id)
        return _to_organization_response(organization)

    async def update_organization(
        self,
        auth: AuthContext,
        organization_id: uuid.UUID,
        body: UpdateOrganizationRequest,
    ) -> OrganizationResponse:
        role = auth.require_membership(organization_id)
        if not can_manage_organization(role):
            raise ForbiddenError(message="only owners can update the organization")

        organization = await self._require_organization(organization_id)
        if body.slug is not None and body.slug != organization.slug:
            existing = await self.organizations.get_by_slug(body.slug)
            if existing is not None:
                raise DuplicateOrganizationSlugError(slug=body.slug)
            organization.slug = body.slug
        if body.name is not None:
            organization.name = body.name
        updated = await self.organizations.save(organization)
        return _to_organization_response(updated)

    async def add_member(
        self,
        auth: AuthContext,
        organization_id: uuid.UUID,
        body: AddOrganizationMemberRequest,
    ) -> OrganizationMemberResponse:
        role = auth.require_membership(organization_id)
        if not can_manage_members(role):
            raise ForbiddenError(message="insufficient permissions to add members")
        if body.role == OrganizationRole.OWNER:
            raise ForbiddenError(message="cannot assign owner role via this endpoint")

        await self._require_organization(organization_id)
        user = await self.users.get_by_id(body.user_id)
        if user is None:
            raise UserNotFoundError(user_id=str(body.user_id))

        existing = await self.members.get_membership(
            organization_id=organization_id,
            user_id=body.user_id,
        )
        if existing is not None:
            existing.role = body.role
            await self.members.save(existing)
            membership = existing
        else:
            membership = await self.members.add_member(
                organization_id=organization_id,
                user_id=body.user_id,
                role=body.role,
            )
            notifications = NotificationService.from_session(self.members._session)
            organization = await self._require_organization(organization_id)
            await notifications.create_notification(
                user_id=body.user_id,
                notification_type=NotificationType.ORGANIZATION_INVITATION,
                title="Organization invitation",
                message=f"You were added to {organization.name}.",
                organization_id=organization_id,
                entity_type="organization",
                entity_id=organization_id,
            )

        audit = AuditService.from_session(self.members._session)
        await audit.record(
            action="organization.member.add",
            entity_type="organization_member",
            entity_id=body.user_id,
            user_id=auth.user.id,
            organization_id=organization_id,
            metadata={"role": body.role.value},
        )

        return OrganizationMemberResponse(
            user_id=membership.user_id,
            organization_id=membership.organization_id,
            role=membership.role.value,
            email=user.email,
            full_name=user.full_name,
        )

    async def list_members(
        self,
        auth: AuthContext,
        organization_id: uuid.UUID,
    ) -> OrganizationMemberListResponse:
        auth.require_membership(organization_id)
        await self._require_organization(organization_id)
        memberships = await self.members.list_for_organization(organization_id)
        return OrganizationMemberListResponse(
            items=[_to_member_response(membership) for membership in memberships],
        )

    async def transfer_ownership(
        self,
        auth: AuthContext,
        organization_id: uuid.UUID,
        body: TransferOwnershipRequest,
    ) -> OrganizationMemberListResponse:
        role = auth.require_membership(organization_id)
        if not can_manage_organization(role):
            raise ForbiddenError(message="only the owner can transfer ownership")

        await self._require_organization(organization_id)
        if body.new_owner_user_id == auth.user.id:
            raise ForbiddenError(message="you are already the organization owner")

        new_owner_membership = await self.members.get_membership(
            organization_id=organization_id,
            user_id=body.new_owner_user_id,
        )
        if new_owner_membership is None:
            raise MemberNotFoundError(
                user_id=str(body.new_owner_user_id),
                organization_id=str(organization_id),
            )

        current_owner = await self.members.get_membership(
            organization_id=organization_id,
            user_id=auth.user.id,
        )
        if current_owner is None:
            raise MemberNotFoundError(
                user_id=str(auth.user.id),
                organization_id=str(organization_id),
            )

        current_owner.role = OrganizationRole.ADMIN
        new_owner_membership.role = OrganizationRole.OWNER
        await self.members.save(current_owner)
        await self.members.save(new_owner_membership)

        audit = AuditService.from_session(self.members._session)
        await audit.record(
            action="organization.ownership.transfer",
            entity_type="organization",
            entity_id=organization_id,
            user_id=auth.user.id,
            organization_id=organization_id,
            metadata={"newOwnerUserId": str(body.new_owner_user_id)},
        )

        memberships = await self.members.list_for_organization(organization_id)
        return OrganizationMemberListResponse(
            items=[_to_member_response(membership) for membership in memberships],
        )

    async def remove_member(
        self,
        auth: AuthContext,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        role = auth.require_membership(organization_id)
        if not can_manage_members(role):
            raise ForbiddenError(message="insufficient permissions to remove members")

        membership = await self.members.get_membership(
            organization_id=organization_id,
            user_id=user_id,
        )
        if membership is None:
            raise MemberNotFoundError(
                user_id=str(user_id),
                organization_id=str(organization_id),
            )
        if membership.role == OrganizationRole.OWNER:
            raise ForbiddenError(message="cannot remove the organization owner")

        await self.members.delete_membership(
            organization_id=organization_id,
            user_id=user_id,
        )
        audit = AuditService.from_session(self.members._session)
        await audit.record(
            action="organization.member.remove",
            entity_type="organization_member",
            entity_id=user_id,
            user_id=auth.user.id,
            organization_id=organization_id,
        )

    async def _require_organization(
        self,
        organization_id: uuid.UUID,
    ) -> Organization:
        organization = await self.organizations.get_by_id(organization_id)
        if organization is None:
            raise OrganizationNotFoundError(organization_id=str(organization_id))
        return organization
