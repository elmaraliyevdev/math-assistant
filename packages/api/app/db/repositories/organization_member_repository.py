"""Organization membership repository."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.organization_member import OrganizationMember, OrganizationRole
from app.db.repositories.base import BaseRepository


class OrganizationMemberRepository(BaseRepository[OrganizationMember]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, OrganizationMember)

    async def get_membership(
        self,
        *,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> OrganizationMember | None:
        result = await self._session.scalars(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == user_id,
            ),
        )
        return result.first()

    async def list_for_user(self, user_id: uuid.UUID) -> list[OrganizationMember]:
        result = await self._session.scalars(
            select(OrganizationMember).where(OrganizationMember.user_id == user_id),
        )
        return list(result.all())

    async def list_for_organization(
        self,
        organization_id: uuid.UUID,
    ) -> list[OrganizationMember]:
        result = await self._session.scalars(
            select(OrganizationMember)
            .options(selectinload(OrganizationMember.user))
            .where(OrganizationMember.organization_id == organization_id),
        )
        return list(result.all())

    async def delete_membership(
        self,
        *,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        membership = await self.get_membership(
            organization_id=organization_id,
            user_id=user_id,
        )
        if membership is not None:
            await self._session.delete(membership)
            await self._session.flush()

    async def add_member(
        self,
        *,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        role: OrganizationRole,
    ) -> OrganizationMember:
        member = OrganizationMember(
            organization_id=organization_id,
            user_id=user_id,
            role=role,
        )
        self._session.add(member)
        await self._session.flush()
        return member
