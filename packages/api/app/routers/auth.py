"""Authentication router."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_auth_context, get_current_user, oauth2_scheme
from app.auth.security_deps import (
    enforce_auth_rate_limit,
    get_client_ip,
)
from app.config import Settings
from app.dependencies import get_audit_service, get_auth_service, get_settings
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    MeResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_auth_rate_limit)],
)
async def register(
    body: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> RegisterResponse:
    return await auth_service.register(body)


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(enforce_auth_rate_limit)],
)
async def login(
    body: LoginRequest,
    client_ip: str = Depends(get_client_ip),
    auth_service: AuthService = Depends(get_auth_service),
    audit_service: AuditService = Depends(get_audit_service),
) -> TokenResponse:
    tokens = await auth_service.login(body, client_ip=client_ip)
    user = await auth_service.users.get_by_email(body.email.strip().lower())
    if user is not None:
        await audit_service.record(
            action="auth.login",
            entity_type="user",
            entity_id=user.id,
            user_id=user.id,
        )
    return tokens


@router.post(
    "/refresh",
    response_model=TokenResponse,
    dependencies=[Depends(enforce_auth_rate_limit)],
)
async def refresh_tokens(
    body: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await auth_service.refresh(body.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(enforce_auth_rate_limit)],
)
async def logout(
    body: LogoutRequest,
    auth_service: AuthService = Depends(get_auth_service),
    audit_service: AuditService = Depends(get_audit_service),
    token: str | None = Depends(oauth2_scheme),
    settings: Settings = Depends(get_settings),
) -> None:
    from app.security.jwt import TokenError, parse_access_token

    await auth_service.logout(body.refresh_token)
    if token is not None:
        try:
            claims = parse_access_token(settings, token)
            await audit_service.record(
                action="auth.logout",
                entity_type="user",
                entity_id=uuid.UUID(claims.sub),
                user_id=uuid.UUID(claims.sub),
            )
        except TokenError:
            pass


@router.get("/me", response_model=MeResponse)
async def get_me(
    auth_service: AuthService = Depends(get_auth_service),
    user=Depends(get_current_user),
) -> MeResponse:
    return await auth_service.get_me(user)
