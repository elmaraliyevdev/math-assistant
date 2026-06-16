"""Authentication dependencies."""

from __future__ import annotations

import uuid
from collections.abc import Callable

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import AuthContext
from app.config import Settings
from app.db.models.organization_member import OrganizationRole
from app.db.repositories.organization_member_repository import OrganizationMemberRepository
from app.db.repositories.user_repository import UserRepository
from app.dependencies import get_db_session, get_settings
from app.exceptions.domain import InactiveUserError, UnauthorizedError
from app.security.jwt import TokenError, parse_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
):
    from app.db.models.user import User

    if token is None:
        raise UnauthorizedError()
    try:
        claims = parse_access_token(settings, token)
    except TokenError as exc:
        raise UnauthorizedError(message="invalid or expired access token") from exc

    user = await UserRepository(session).get_by_id(uuid.UUID(claims.sub))
    if user is None:
        raise UnauthorizedError(message="invalid or expired access token")
    if not user.is_active:
        raise InactiveUserError()
    return user


async def get_auth_context(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> AuthContext:
    memberships = await OrganizationMemberRepository(session).list_for_user(user.id)
    return AuthContext(
        user=user,
        memberships={member.organization_id: member.role for member in memberships},
    )


def require_role(minimum_role: OrganizationRole) -> Callable[..., AuthContext]:
    async def dependency(
        organization_id: uuid.UUID,
        auth: AuthContext = Depends(get_auth_context),
    ) -> AuthContext:
        auth.require_role(organization_id, minimum_role)
        return auth

    return dependency
