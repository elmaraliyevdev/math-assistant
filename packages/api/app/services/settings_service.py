"""User settings and preferences service."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import AuthContext
from app.db.repositories.user_preferences_repository import UserPreferencesRepository
from app.db.repositories.user_repository import UserRepository
from app.exceptions.domain import InvalidCredentialsError
from app.schemas.auth import UserResponse
from app.schemas.platform import (
    UpdateProfileRequest,
    UpdateUserPreferencesRequest,
    UserPreferencesResponse,
)
from app.security.passwords import hash_password, verify_password


def _to_preferences_response(preferences) -> UserPreferencesResponse:
    return UserPreferencesResponse(
        theme=preferences.theme,
        notify_simulation_completed=preferences.notify_simulation_completed,
        notify_simulation_failed=preferences.notify_simulation_failed,
        notify_validation_failed=preferences.notify_validation_failed,
        notify_organization_invitation=preferences.notify_organization_invitation,
    )


@dataclass(frozen=True, slots=True)
class SettingsService:
    users: UserRepository
    preferences: UserPreferencesRepository

    @classmethod
    def from_session(cls, session: AsyncSession) -> SettingsService:
        return cls(
            users=UserRepository(session),
            preferences=UserPreferencesRepository(session),
        )

    async def get_preferences(self, auth: AuthContext) -> UserPreferencesResponse:
        prefs = await self.preferences.get_or_create(auth.user_id)
        return _to_preferences_response(prefs)

    async def update_preferences(
        self,
        auth: AuthContext,
        body: UpdateUserPreferencesRequest,
    ) -> UserPreferencesResponse:
        prefs = await self.preferences.get_or_create(auth.user_id)
        if body.theme is not None:
            prefs.theme = body.theme
        if body.notify_simulation_completed is not None:
            prefs.notify_simulation_completed = body.notify_simulation_completed
        if body.notify_simulation_failed is not None:
            prefs.notify_simulation_failed = body.notify_simulation_failed
        if body.notify_validation_failed is not None:
            prefs.notify_validation_failed = body.notify_validation_failed
        if body.notify_organization_invitation is not None:
            prefs.notify_organization_invitation = body.notify_organization_invitation
        await self.preferences.save(prefs)
        return _to_preferences_response(prefs)

    async def update_profile(
        self,
        auth: AuthContext,
        body: UpdateProfileRequest,
    ) -> UserResponse:
        user = await self.users.get_by_id(auth.user_id)
        if user is None:
            raise InvalidCredentialsError()
        if body.full_name is not None:
            user.full_name = body.full_name.strip()
        await self.users.save(user)
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def change_password(
        self,
        auth: AuthContext,
        *,
        current_password: str,
        new_password: str,
    ) -> None:
        user = await self.users.get_by_id(auth.user_id)
        if user is None or not verify_password(current_password, user.password_hash):
            raise InvalidCredentialsError()
        user.password_hash = hash_password(new_password)
        await self.users.save(user)
