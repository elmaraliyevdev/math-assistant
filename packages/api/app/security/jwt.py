"""JWT token utilities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.config import Settings


class TokenError(Exception):
    """Raised when a token cannot be validated."""


@dataclass(frozen=True, slots=True)
class AccessTokenClaims:
    sub: str
    email: str
    exp: datetime
    type: str


@dataclass(frozen=True, slots=True)
class RefreshTokenClaims:
    sub: str
    jti: str
    exp: datetime
    type: str


def create_access_token(
    *,
    settings: Settings,
    user_id: uuid.UUID,
    email: str,
) -> str:
    expires_at = datetime.now(tz=UTC) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes,
    )
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expires_at,
        "type": "access",
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(
    *,
    settings: Settings,
    user_id: uuid.UUID,
    jti: str,
) -> str:
    expires_at = datetime.now(tz=UTC) + timedelta(
        days=settings.jwt_refresh_token_expire_days,
    )
    payload = {
        "sub": str(user_id),
        "jti": jti,
        "exp": expires_at,
        "type": "refresh",
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(settings: Settings, token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError as exc:
        msg = "invalid token"
        raise TokenError(msg) from exc


def parse_access_token(settings: Settings, token: str) -> AccessTokenClaims:
    payload = decode_token(settings, token)
    if payload.get("type") != "access":
        msg = "invalid access token"
        raise TokenError(msg)
    return AccessTokenClaims(
        sub=str(payload["sub"]),
        email=str(payload["email"]),
        exp=datetime.fromtimestamp(payload["exp"], tz=UTC),
        type="access",
    )


def parse_refresh_token(settings: Settings, token: str) -> RefreshTokenClaims:
    payload = decode_token(settings, token)
    if payload.get("type") != "refresh":
        msg = "invalid refresh token"
        raise TokenError(msg)
    return RefreshTokenClaims(
        sub=str(payload["sub"]),
        jti=str(payload["jti"]),
        exp=datetime.fromtimestamp(payload["exp"], tz=UTC),
        type="refresh",
    )
