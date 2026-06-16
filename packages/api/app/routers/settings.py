"""User settings router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_auth_context
from app.auth.context import AuthContext
from app.dependencies import get_settings_service
from app.schemas.auth import UserResponse
from app.schemas.platform import (
    ChangePasswordRequest,
    UpdateProfileRequest,
    UpdateUserPreferencesRequest,
    UserPreferencesResponse,
)
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/users/me", tags=["settings"])


@router.get("/preferences", response_model=UserPreferencesResponse)
async def get_preferences(
    auth: AuthContext = Depends(get_auth_context),
    settings_service: SettingsService = Depends(get_settings_service),
) -> UserPreferencesResponse:
    return await settings_service.get_preferences(auth)


@router.patch("/preferences", response_model=UserPreferencesResponse)
async def update_preferences(
    body: UpdateUserPreferencesRequest,
    auth: AuthContext = Depends(get_auth_context),
    settings_service: SettingsService = Depends(get_settings_service),
) -> UserPreferencesResponse:
    return await settings_service.update_preferences(auth, body)


@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    body: UpdateProfileRequest,
    auth: AuthContext = Depends(get_auth_context),
    settings_service: SettingsService = Depends(get_settings_service),
) -> UserResponse:
    return await settings_service.update_profile(auth, body)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    body: ChangePasswordRequest,
    auth: AuthContext = Depends(get_auth_context),
    settings_service: SettingsService = Depends(get_settings_service),
) -> None:
    await settings_service.change_password(
        auth,
        current_password=body.current_password,
        new_password=body.new_password,
    )
