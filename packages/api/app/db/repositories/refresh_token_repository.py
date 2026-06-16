"""Refresh token repository."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.refresh_token import RefreshToken
from app.db.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RefreshToken)

    async def get_by_jti(self, jti: str) -> RefreshToken | None:
        result = await self._session.scalars(
            select(RefreshToken).where(RefreshToken.jti == jti),
        )
        return result.first()

    async def revoke(self, token: RefreshToken) -> None:
        token.revoked_at = datetime.now(tz=UTC)
        await self.save(token)

    async def revoke_all_for_user(self, user_id) -> int:
        result = await self._session.scalars(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            ),
        )
        tokens = list(result)
        now = datetime.now(tz=UTC)
        for token in tokens:
            token.revoked_at = now
        if tokens:
            await self._session.flush()
        return len(tokens)
