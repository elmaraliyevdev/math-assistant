"""Contact submission repository."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.contact_submission import ContactSubmission
from app.db.repositories.base import BaseRepository


class ContactSubmissionRepository(BaseRepository[ContactSubmission]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ContactSubmission)

    async def list_recent(self, *, limit: int = 100, offset: int = 0) -> list[ContactSubmission]:
        result = await self._session.scalars(
            select(ContactSubmission)
            .order_by(ContactSubmission.created_at.desc())
            .limit(limit)
            .offset(offset),
        )
        return list(result.all())

    async def count_all(self) -> int:
        result = await self._session.scalar(
            select(func.count()).select_from(ContactSubmission),
        )
        return int(result or 0)
