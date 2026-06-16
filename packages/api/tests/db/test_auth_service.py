"""Authentication service unit tests."""

from __future__ import annotations

import pytest

from app.config import Settings
from app.exceptions.domain import (
    DuplicateEmailError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService, _slugify


def test_slugify_special_characters() -> None:
    assert _slugify("  Hello World!!  ") == "hello-world"
    assert _slugify("!!!") == "workspace"


@pytest.mark.asyncio
async def test_register_creates_user_and_workspace(db_session) -> None:
    settings = Settings(jwt_secret_key="test-secret-key")
    service = AuthService.from_session(db_session, settings)
    response = await service.register(
        RegisterRequest(
            email="new-user@example.com",
            password="secure-password",
            fullName="New User",
        ),
    )
    assert response.user.email == "new-user@example.com"
    assert response.organization_id is not None
    assert response.tokens.access_token


@pytest.mark.asyncio
async def test_register_duplicate_email(db_session, sample_user, user_repo) -> None:
    await user_repo.add(sample_user)
    settings = Settings(jwt_secret_key="test-secret-key")
    service = AuthService.from_session(db_session, settings)
    with pytest.raises(DuplicateEmailError):
        await service.register(
            RegisterRequest(
                email=sample_user.email,
                password="secure-password",
                fullName="Duplicate",
            ),
        )


@pytest.mark.asyncio
async def test_login_success(db_session, sample_user, user_repo) -> None:
    await user_repo.add(sample_user)
    settings = Settings(jwt_secret_key="test-secret-key")
    service = AuthService.from_session(db_session, settings)
    tokens = await service.login(
        LoginRequest(email=sample_user.email, password="secure-password"),
        client_ip="127.0.0.1",
    )
    assert tokens.access_token


@pytest.mark.asyncio
async def test_login_invalid_credentials(db_session) -> None:
    settings = Settings(jwt_secret_key="test-secret-key")
    service = AuthService.from_session(db_session, settings)
    with pytest.raises(InvalidCredentialsError):
        await service.login(
            LoginRequest(email="missing@example.com", password="wrong"),
            client_ip="127.0.0.1",
        )


@pytest.mark.asyncio
async def test_refresh_invalid_token(db_session) -> None:
    settings = Settings(jwt_secret_key="test-secret-key")
    service = AuthService.from_session(db_session, settings)
    with pytest.raises(InvalidTokenError):
        await service.refresh("not-a-valid-token")


@pytest.mark.asyncio
async def test_get_me_returns_memberships(
    db_session,
    auth_context,
) -> None:
    settings = Settings(jwt_secret_key="test-secret-key")
    service = AuthService.from_session(db_session, settings)
    me = await service.get_me(auth_context.user)
    assert me.user.id == auth_context.user.id
    assert len(me.organizations) == 1


@pytest.mark.asyncio
async def test_refresh_rotates_tokens(db_session, sample_user, user_repo) -> None:
    await user_repo.add(sample_user)
    settings = Settings(jwt_secret_key="test-secret-key")
    service = AuthService.from_session(db_session, settings)
    issued = await service.login(
        LoginRequest(email=sample_user.email, password="secure-password"),
        client_ip="127.0.0.1",
    )
    refreshed = await service.refresh(issued.refresh_token)
    assert refreshed.access_token
    assert refreshed.refresh_token != issued.refresh_token


@pytest.mark.asyncio
async def test_login_inactive_user(db_session, sample_user, user_repo) -> None:
    sample_user.is_active = False
    await user_repo.add(sample_user)
    settings = Settings(jwt_secret_key="test-secret-key")
    service = AuthService.from_session(db_session, settings)
    with pytest.raises(InactiveUserError):
        await service.login(
            LoginRequest(email=sample_user.email, password="secure-password"),
            client_ip="127.0.0.1",
        )


@pytest.mark.asyncio
async def test_register_uses_incremented_slug_when_taken(
    db_session,
    organization_repo,
    sample_organization,
) -> None:
    await organization_repo.add(sample_organization)
    settings = Settings(jwt_secret_key="test-secret-key")
    service = AuthService.from_session(db_session, settings)
    response = await service.register(
        RegisterRequest(
            email="slug-user@example.com",
            password="secure-password",
            fullName=sample_organization.name,
        ),
    )
    assert response.user.email == "slug-user@example.com"
