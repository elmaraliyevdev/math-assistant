"""Organization repository."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.organization import Organization
from app.db.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Organization)

    async def get_by_slug(self, slug: str) -> Organization | None:
        result = await self._session.scalars(
            select(Organization).where(Organization.slug == slug),
        )
        return result.first()

    async def list_for_user(self, user_id: uuid.UUID) -> list[Organization]:
        from app.db.models.organization_member import OrganizationMember

        stmt = (
            select(Organization)
            .join(OrganizationMember)
            .where(OrganizationMember.user_id == user_id)
            .order_by(Organization.created_at.asc())
        )
        result = await self._session.scalars(stmt)
        return list(result.all())
