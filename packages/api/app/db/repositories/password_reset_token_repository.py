"""Password reset token repository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.password_reset_token import PasswordResetToken
from app.db.repositories.base import BaseRepository


class PasswordResetTokenRepository(BaseRepository[PasswordResetToken]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, PasswordResetToken)

    async def get_by_hash(self, token_hash: str) -> PasswordResetToken | None:
        result = await self._session.scalars(
            select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash),
        )
        return result.first()
