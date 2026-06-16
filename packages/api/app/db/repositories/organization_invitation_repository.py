"""Organization invitation repository."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.organization_invitation import (
    InvitationStatus,
    OrganizationInvitation,
)
from app.db.repositories.base import BaseRepository
from app.db.models.organization_member import OrganizationRole
from app.util.datetime import normalize_utc, utc_now


class OrganizationInvitationRepository(BaseRepository[OrganizationInvitation]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, OrganizationInvitation)

    async def get_by_id(self, invitation_id: uuid.UUID) -> OrganizationInvitation | None:
        result = await self._session.scalars(
            select(OrganizationInvitation)
            .options(selectinload(OrganizationInvitation.organization))
            .where(OrganizationInvitation.id == invitation_id),
        )
        return result.first()

    async def get_pending_for_organization_email(
        self,
        *,
        organization_id: uuid.UUID,
        email: str,
    ) -> OrganizationInvitation | None:
        normalized = email.strip().lower()
        result = await self._session.scalars(
            select(OrganizationInvitation).where(
                OrganizationInvitation.organization_id == organization_id,
                OrganizationInvitation.email == normalized,
                OrganizationInvitation.status == InvitationStatus.PENDING,
            ),
        )
        return result.first()

    async def list_pending_for_organization(
        self,
        organization_id: uuid.UUID,
    ) -> list[OrganizationInvitation]:
        result = await self._session.scalars(
            select(OrganizationInvitation)
            .where(
                OrganizationInvitation.organization_id == organization_id,
                OrganizationInvitation.status == InvitationStatus.PENDING,
            )
            .order_by(OrganizationInvitation.created_at.desc()),
        )
        return list(result.all())

    async def list_pending_for_email(self, email: str) -> list[OrganizationInvitation]:
        normalized = email.strip().lower()
        result = await self._session.scalars(
            select(OrganizationInvitation)
            .options(selectinload(OrganizationInvitation.organization))
            .where(
                OrganizationInvitation.email == normalized,
                OrganizationInvitation.status == InvitationStatus.PENDING,
            )
            .order_by(OrganizationInvitation.created_at.desc()),
        )
        return list(result.all())

    async def create_invitation(
        self,
        *,
        organization_id: uuid.UUID,
        email: str,
        role: OrganizationRole,
        invited_by_user_id: uuid.UUID,
        expires_at: datetime,
    ) -> OrganizationInvitation:
        invitation = OrganizationInvitation(
            organization_id=organization_id,
            email=email.strip().lower(),
            role=role,
            invited_by_user_id=invited_by_user_id,
            status=InvitationStatus.PENDING,
            expires_at=expires_at,
        )
        self._session.add(invitation)
        await self._session.flush()
        return invitation

    async def expire_stale_pending(self) -> int:
        now = utc_now()
        result = await self._session.scalars(
            select(OrganizationInvitation).where(
                OrganizationInvitation.status == InvitationStatus.PENDING,
            ),
        )
        invitations = list(result.all())
        expired_count = 0
        for invitation in invitations:
            if normalize_utc(invitation.expires_at) <= now:
                invitation.status = InvitationStatus.EXPIRED
                expired_count += 1
        if expired_count:
            await self._session.flush()
        return expired_count
