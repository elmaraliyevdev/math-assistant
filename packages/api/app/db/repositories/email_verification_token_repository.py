"""Email verification token repository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.email_verification_token import EmailVerificationToken
from app.db.repositories.base import BaseRepository


class EmailVerificationTokenRepository(BaseRepository[EmailVerificationToken]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, EmailVerificationToken)

    async def get_by_hash(self, token_hash: str) -> EmailVerificationToken | None:
        result = await self._session.scalars(
            select(EmailVerificationToken).where(
                EmailVerificationToken.token_hash == token_hash,
            ),
        )
        return result.first()
