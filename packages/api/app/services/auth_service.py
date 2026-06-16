"""Authentication service."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.db.models.organization import Organization
from app.db.models.organization_member import OrganizationMember, OrganizationRole
from app.db.models.refresh_token import RefreshToken
from app.db.models.user import User
from app.db.repositories.organization_member_repository import OrganizationMemberRepository
from app.db.repositories.organization_repository import OrganizationRepository
from app.db.repositories.refresh_token_repository import RefreshTokenRepository
from app.db.repositories.user_repository import UserRepository
from app.exceptions.domain import (
    DuplicateEmailError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from app.schemas.auth import (
    LoginRequest,
    MeResponse,
    OrganizationMembershipResponse,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserResponse,
)
from app.security.jwt import (
    TokenError,
    create_access_token,
    create_refresh_token,
    parse_refresh_token,
)
from app.security.passwords import hash_password, verify_password


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "workspace"


def _to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@dataclass(frozen=True, slots=True)
class AuthService:
    users: UserRepository
    organizations: OrganizationRepository
    members: OrganizationMemberRepository
    refresh_tokens: RefreshTokenRepository
    settings: Settings

    @classmethod
    def from_session(cls, session: AsyncSession, settings: Settings) -> AuthService:
        return cls(
            users=UserRepository(session),
            organizations=OrganizationRepository(session),
            members=OrganizationMemberRepository(session),
            refresh_tokens=RefreshTokenRepository(session),
            settings=settings,
        )

    async def register(self, body: RegisterRequest) -> RegisterResponse:
        email = body.email.strip().lower()
        existing = await self.users.get_by_email(email)
        if existing is not None:
            raise DuplicateEmailError(email=email)

        user = User(
            email=email,
            password_hash=hash_password(body.password),
            full_name=body.full_name.strip(),
            is_active=True,
        )
        await self.users.add(user)

        base_slug = _slugify(body.full_name)
        slug = base_slug
        suffix = 1
        while await self.organizations.get_by_slug(slug) is not None:
            slug = f"{base_slug}-{suffix}"
            suffix += 1

        organization = Organization(
            name=f"{body.full_name.strip()}'s Workspace",
            slug=slug,
        )
        await self.organizations.add(organization)
        await self.members.add_member(
            organization_id=organization.id,
            user_id=user.id,
            role=OrganizationRole.OWNER,
        )

        tokens = await self._issue_tokens(user)
        return RegisterResponse(
            user=_to_user_response(user),
            organization_id=organization.id,
            tokens=tokens,
        )

    async def login(self, body: LoginRequest, *, client_ip: str) -> TokenResponse:
        from app.security.guards import get_brute_force_guard

        guard = get_brute_force_guard()
        guard.check_allowed(body.email, client_ip)
        user = await self.users.get_by_email(body.email)
        if user is None or not verify_password(body.password, user.password_hash):
            guard.record_failure(body.email, client_ip)
            raise InvalidCredentialsError
        if not user.is_active:
            raise InactiveUserError
        guard.record_success(body.email, client_ip)
        return await self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        claims = self._parse_refresh(refresh_token)
        stored = await self.refresh_tokens.get_by_jti(claims.jti)
        if stored is None:
            raise InvalidTokenError()
        if stored.revoked_at is not None:
            await self.refresh_tokens.revoke_all_for_user(stored.user_id)
            raise InvalidTokenError(message="refresh token reuse detected")
        expires_at = stored.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at <= datetime.now(tz=UTC):
            raise InvalidTokenError(message="refresh token expired")

        user = await self.users.get_by_id(uuid.UUID(claims.sub))
        if user is None or not user.is_active:
            raise InvalidTokenError()

        await self.refresh_tokens.revoke(stored)
        return await self._issue_tokens(user)

    async def logout(self, refresh_token: str) -> None:
        claims = self._parse_refresh(refresh_token)
        stored = await self.refresh_tokens.get_by_jti(claims.jti)
        if stored is not None and stored.revoked_at is None:
            await self.refresh_tokens.revoke(stored)

    async def get_me(self, user: User) -> MeResponse:
        memberships = await self.members.list_for_user(user.id)
        organizations: list[OrganizationMembershipResponse] = []
        for membership in memberships:
            organization = await self.organizations.get_by_id(
                membership.organization_id,
            )
            if organization is None:
                continue
            organizations.append(
                OrganizationMembershipResponse(
                    organization_id=organization.id,
                    organization_name=organization.name,
                    organization_slug=organization.slug,
                    role=membership.role.value,
                ),
            )
        return MeResponse(user=_to_user_response(user), organizations=organizations)

    async def _issue_tokens(self, user: User) -> TokenResponse:
        jti = uuid.uuid4().hex
        refresh_token = create_refresh_token(
            settings=self.settings,
            user_id=user.id,
            jti=jti,
        )
        expires_at = datetime.now(tz=UTC) + timedelta(
            days=self.settings.jwt_refresh_token_expire_days,
        )
        await self.refresh_tokens.add(
            RefreshToken(
                user_id=user.id,
                jti=jti,
                expires_at=expires_at,
            ),
        )
        access_token = create_access_token(
            settings=self.settings,
            user_id=user.id,
            email=user.email,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.settings.jwt_access_token_expire_minutes * 60,
        )

    def _parse_refresh(self, refresh_token: str):
        try:
            return parse_refresh_token(self.settings, refresh_token)
        except TokenError as exc:
            raise InvalidTokenError() from exc
