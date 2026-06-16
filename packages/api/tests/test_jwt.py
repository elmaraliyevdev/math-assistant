"""JWT helper tests."""

from __future__ import annotations

import uuid

import pytest

from app.config import Settings
from app.security.jwt import (
    TokenError,
    create_access_token,
    create_refresh_token,
    parse_access_token,
    parse_refresh_token,
)


def test_parse_access_and_refresh_tokens() -> None:
    settings = Settings(jwt_secret_key="test-secret-key")
    user_id = uuid.uuid4()
    access = create_access_token(settings=settings, user_id=user_id, email="a@b.com")
    refresh = create_refresh_token(settings=settings, user_id=user_id, jti="jti-1")

    access_claims = parse_access_token(settings, access)
    assert access_claims.email == "a@b.com"

    refresh_claims = parse_refresh_token(settings, refresh)
    assert refresh_claims.jti == "jti-1"


def test_parse_access_token_rejects_refresh_token() -> None:
    settings = Settings(jwt_secret_key="test-secret-key")
    refresh = create_refresh_token(
        settings=settings,
        user_id=uuid.uuid4(),
        jti="jti-2",
    )
    with pytest.raises(TokenError, match="invalid access token"):
        parse_access_token(settings, refresh)


def test_parse_refresh_token_rejects_access_token() -> None:
    settings = Settings(jwt_secret_key="test-secret-key")
    access = create_access_token(
        settings=settings,
        user_id=uuid.uuid4(),
        email="a@b.com",
    )
    with pytest.raises(TokenError, match="invalid refresh token"):
        parse_refresh_token(settings, access)
