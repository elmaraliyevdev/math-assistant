"""Organization email invitation service."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import AuthContext
from app.db.models.notification import NotificationType
from app.db.models.organization_invitation import (
    InvitationStatus,
    OrganizationInvitation,
)
from app.db.models.organization_member import OrganizationRole
from app.db.repositories.organization_invitation_repository import (
    OrganizationInvitationRepository,
)
from app.db.repositories.organization_member_repository import OrganizationMemberRepository
from app.db.repositories.organization_repository import OrganizationRepository
from app.db.repositories.user_repository import UserRepository
from app.exceptions.domain import (
    AlreadyOrganizationMemberError,
    DuplicateInvitationError,
    ForbiddenError,
    InvitationEmailMismatchError,
    InvitationExpiredError,
    InvitationNotFoundError,
    OrganizationNotFoundError,
)
from app.schemas.organizations import (
    OrganizationInvitationListResponse,
    OrganizationInvitationResponse,
)
from app.security.permissions import can_manage_members
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService

from app.util.datetime import normalize_utc, utc_now

INVITATION_TTL_DAYS = 7


def _to_invitation_response(
    invitation: OrganizationInvitation,
    *,
    organization_name: str,
) -> OrganizationInvitationResponse:
    return OrganizationInvitationResponse(
        id=invitation.id,
        organization_id=invitation.organization_id,
        organization_name=organization_name,
        email=invitation.email,
        role=invitation.role.value,
        status=invitation.status.value,
        invited_by_user_id=invitation.invited_by_user_id,
        expires_at=invitation.expires_at,
        created_at=invitation.created_at,
        accepted_at=invitation.accepted_at,
    )


@dataclass(frozen=True, slots=True)
class InvitationService:
    invitations: OrganizationInvitationRepository
    organizations: OrganizationRepository
    members: OrganizationMemberRepository
    users: UserRepository

    @classmethod
    def from_session(cls, session: AsyncSession) -> InvitationService:
        return cls(
            invitations=OrganizationInvitationRepository(session),
            organizations=OrganizationRepository(session),
            members=OrganizationMemberRepository(session),
            users=UserRepository(session),
        )

    async def create_invitation(
        self,
        auth: AuthContext,
        organization_id: uuid.UUID,
        *,
        email: str,
        role: OrganizationRole,
    ) -> OrganizationInvitationResponse:
        member_role = auth.require_membership(organization_id)
        if not can_manage_members(member_role):
            raise ForbiddenError(message="insufficient permissions to invite members")
        if role == OrganizationRole.OWNER:
            raise ForbiddenError(message="cannot invite members as owner")

        organization = await self.organizations.get_by_id(organization_id)
        if organization is None:
            raise OrganizationNotFoundError(organization_id=str(organization_id))

        normalized_email = email.strip().lower()
        existing_user = await self.users.get_by_email(normalized_email)
        if existing_user is not None:
            membership = await self.members.get_membership(
                organization_id=organization_id,
                user_id=existing_user.id,
            )
            if membership is not None:
                raise AlreadyOrganizationMemberError(
                    email=normalized_email,
                    organization_id=str(organization_id),
                )

        await self.invitations.expire_stale_pending()
        pending = await self.invitations.get_pending_for_organization_email(
            organization_id=organization_id,
            email=normalized_email,
        )
        if pending is not None:
            raise DuplicateInvitationError(
                email=normalized_email,
                organization_id=str(organization_id),
            )

        expires_at = utc_now() + timedelta(days=INVITATION_TTL_DAYS)
        invitation = await self.invitations.create_invitation(
            organization_id=organization_id,
            email=normalized_email,
            role=role,
            invited_by_user_id=auth.user.id,
            expires_at=expires_at,
        )

        if existing_user is not None:
            notifications = NotificationService.from_session(self.invitations._session)
            await notifications.create_notification(
                user_id=existing_user.id,
                notification_type=NotificationType.ORGANIZATION_INVITATION,
                title="Organization invitation",
                message=f"You were invited to join {organization.name}.",
                organization_id=organization_id,
                entity_type="organization_invitation",
                entity_id=invitation.id,
            )

        audit = AuditService.from_session(self.invitations._session)
        await audit.record(
            action="organization.invitation.create",
            entity_type="organization_invitation",
            entity_id=invitation.id,
            user_id=auth.user.id,
            organization_id=organization_id,
            metadata={"email": normalized_email, "role": role.value},
        )

        return _to_invitation_response(
            invitation,
            organization_name=organization.name,
        )

    async def list_organization_invitations(
        self,
        auth: AuthContext,
        organization_id: uuid.UUID,
    ) -> OrganizationInvitationListResponse:
        member_role = auth.require_membership(organization_id)
        if not can_manage_members(member_role):
            raise ForbiddenError(message="insufficient permissions to view invitations")

        organization = await self.organizations.get_by_id(organization_id)
        if organization is None:
            raise OrganizationNotFoundError(organization_id=str(organization_id))

        await self.invitations.expire_stale_pending()
        invitations = await self.invitations.list_pending_for_organization(
            organization_id,
        )
        return OrganizationInvitationListResponse(
            items=[
                _to_invitation_response(
                    invitation,
                    organization_name=organization.name,
                )
                for invitation in invitations
            ],
        )

    async def list_my_invitations(
        self,
        auth: AuthContext,
    ) -> OrganizationInvitationListResponse:
        await self.invitations.expire_stale_pending()
        invitations = await self.invitations.list_pending_for_email(auth.user.email)
        items: list[OrganizationInvitationResponse] = []
        for invitation in invitations:
            organization = invitation.organization
            if organization is None:
                organization = await self.organizations.get_by_id(
                    invitation.organization_id,
                )
            organization_name = organization.name if organization is not None else ""
            items.append(
                _to_invitation_response(
                    invitation,
                    organization_name=organization_name,
                ),
            )
        return OrganizationInvitationListResponse(items=items)

    async def cancel_invitation(
        self,
        auth: AuthContext,
        organization_id: uuid.UUID,
        invitation_id: uuid.UUID,
    ) -> None:
        member_role = auth.require_membership(organization_id)
        if not can_manage_members(member_role):
            raise ForbiddenError(message="insufficient permissions to cancel invitations")

        invitation = await self.invitations.get_by_id(invitation_id)
        if (
            invitation is None
            or invitation.organization_id != organization_id
            or invitation.status != InvitationStatus.PENDING
        ):
            raise InvitationNotFoundError(invitation_id=str(invitation_id))

        invitation.status = InvitationStatus.CANCELLED
        await self.invitations.save(invitation)

    async def accept_invitation(
        self,
        auth: AuthContext,
        invitation_id: uuid.UUID,
    ) -> OrganizationInvitationResponse:
        invitation = await self._require_actionable_invitation(invitation_id)
        if auth.user.email != invitation.email:
            raise InvitationEmailMismatchError()

        existing = await self.members.get_membership(
            organization_id=invitation.organization_id,
            user_id=auth.user.id,
        )
        if existing is None:
            await self.members.add_member(
                organization_id=invitation.organization_id,
                user_id=auth.user.id,
                role=invitation.role,
            )
        else:
            existing.role = invitation.role
            await self.members.save(existing)

        invitation.status = InvitationStatus.ACCEPTED
        invitation.accepted_at = utc_now()
        await self.invitations.save(invitation)

        organization = invitation.organization
        if organization is None:
            organization = await self.organizations.get_by_id(invitation.organization_id)

        audit = AuditService.from_session(self.invitations._session)
        await audit.record(
            action="organization.invitation.accept",
            entity_type="organization_invitation",
            entity_id=invitation.id,
            user_id=auth.user.id,
            organization_id=invitation.organization_id,
        )

        return _to_invitation_response(
            invitation,
            organization_name=organization.name if organization is not None else "",
        )

    async def decline_invitation(
        self,
        auth: AuthContext,
        invitation_id: uuid.UUID,
    ) -> OrganizationInvitationResponse:
        invitation = await self._require_actionable_invitation(invitation_id)
        if auth.user.email != invitation.email:
            raise InvitationEmailMismatchError()

        invitation.status = InvitationStatus.DECLINED
        await self.invitations.save(invitation)

        organization = invitation.organization
        if organization is None:
            organization = await self.organizations.get_by_id(invitation.organization_id)

        return _to_invitation_response(
            invitation,
            organization_name=organization.name if organization is not None else "",
        )

    async def _require_actionable_invitation(
        self,
        invitation_id: uuid.UUID,
    ) -> OrganizationInvitation:
        await self.invitations.expire_stale_pending()
        invitation = await self.invitations.get_by_id(invitation_id)
        if invitation is None:
            raise InvitationNotFoundError(invitation_id=str(invitation_id))
        if invitation.status == InvitationStatus.EXPIRED:
            raise InvitationExpiredError(invitation_id=str(invitation_id))
        if invitation.status != InvitationStatus.PENDING:
            raise InvitationNotFoundError(invitation_id=str(invitation_id))
        if normalize_utc(invitation.expires_at) <= utc_now():
            invitation.status = InvitationStatus.EXPIRED
            await self.invitations.save(invitation)
            raise InvitationExpiredError(invitation_id=str(invitation_id))
        return invitation
