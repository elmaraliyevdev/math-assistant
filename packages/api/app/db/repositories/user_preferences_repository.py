"""User preferences repository."""

from __future__ import annotations

import uuid

from app.db.models.user_preferences import UserPreferences
from app.db.repositories.base import BaseRepository


class UserPreferencesRepository(BaseRepository[UserPreferences]):
    def __init__(self, session) -> None:
        super().__init__(session, UserPreferences)

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserPreferences | None:
        return await self.get_by_id(user_id)

    async def get_or_create(self, user_id: uuid.UUID) -> UserPreferences:
        existing = await self.get_by_user_id(user_id)
        if existing is not None:
            return existing
        preferences = UserPreferences(user_id=user_id)
        return await self.add(preferences)
