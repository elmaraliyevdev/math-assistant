"""Authentication service."""

from __future__ import annotations

import hashlib
import logging
import re
import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.db.models.email_verification_token import EmailVerificationToken
from app.db.models.organization import Organization
from app.db.models.organization_member import OrganizationMember, OrganizationRole
from app.db.models.password_reset_token import PasswordResetToken
from app.db.models.refresh_token import RefreshToken
from app.db.models.user import User
from app.db.repositories.email_verification_token_repository import (
    EmailVerificationTokenRepository,
)
from app.db.repositories.organization_member_repository import OrganizationMemberRepository
from app.db.repositories.organization_repository import OrganizationRepository
from app.db.repositories.password_reset_token_repository import PasswordResetTokenRepository
from app.db.repositories.refresh_token_repository import RefreshTokenRepository
from app.db.repositories.user_repository import UserRepository
from app.exceptions.domain import (
    DuplicateEmailError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from app.schemas.auth import (
    ForgotPasswordResponse,
    LoginRequest,
    MeResponse,
    OrganizationMembershipResponse,
    RegisterRequest,
    RegisterResponse,
    ResendVerificationResponse,
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

logger = logging.getLogger(__name__)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "workspace"


def _to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        email_verified=user.email_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@dataclass(frozen=True, slots=True)
class AuthService:
    users: UserRepository
    organizations: OrganizationRepository
    members: OrganizationMemberRepository
    refresh_tokens: RefreshTokenRepository
    password_reset_tokens: PasswordResetTokenRepository
    email_verification_tokens: EmailVerificationTokenRepository
    settings: Settings

    @classmethod
    def from_session(cls, session: AsyncSession, settings: Settings) -> AuthService:
        return cls(
            users=UserRepository(session),
            organizations=OrganizationRepository(session),
            members=OrganizationMemberRepository(session),
            refresh_tokens=RefreshTokenRepository(session),
            password_reset_tokens=PasswordResetTokenRepository(session),
            email_verification_tokens=EmailVerificationTokenRepository(session),
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
        await self._create_email_verification_token(user)
        return RegisterResponse(
            user=_to_user_response(user),
            organization_id=organization.id,
            tokens=tokens,
        )

    async def login(
        self,
        body: LoginRequest,
        *,
        client_ip: str,
        remember_me: bool = False,
    ) -> TokenResponse:
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
        return await self._issue_tokens(user, remember_me=remember_me)

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

    async def _issue_tokens(self, user: User, *, remember_me: bool = False) -> TokenResponse:
        jti = uuid.uuid4().hex
        refresh_token = create_refresh_token(
            settings=self.settings,
            user_id=user.id,
            jti=jti,
        )
        refresh_days = self.settings.jwt_refresh_token_expire_days
        if remember_me:
            refresh_days = max(refresh_days, 90)
        expires_at = datetime.now(tz=UTC) + timedelta(days=refresh_days)
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

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    async def forgot_password(self, email: str) -> ForgotPasswordResponse:
        user = await self.users.get_by_email(email)
        if user is not None:
            raw_token = secrets.token_urlsafe(32)
            token_hash = self._hash_token(raw_token)
            expires_at = datetime.now(tz=UTC) + timedelta(hours=1)
            await self.password_reset_tokens.add(
                PasswordResetToken(
                    user_id=user.id,
                    token_hash=token_hash,
                    expires_at=expires_at,
                ),
            )
            reset_url = f"{self.settings.frontend_url}/reset-password?token={raw_token}"
            if self.settings.smtp_enabled:
                logger.info("Password reset link for %s: %s", email, reset_url)
            else:
                logger.info("Password reset link (dev) for %s: %s", email, reset_url)
        return ForgotPasswordResponse(
            message="If an account exists for this email, a reset link has been sent.",
        )

    async def reset_password(self, token: str, password: str) -> None:
        token_hash = self._hash_token(token)
        stored = await self.password_reset_tokens.get_by_hash(token_hash)
        if stored is None or stored.used_at is not None:
            raise InvalidTokenError(message="invalid or expired reset token")
        expires_at = stored.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at <= datetime.now(tz=UTC):
            raise InvalidTokenError(message="invalid or expired reset token")

        user = await self.users.get_by_id(stored.user_id)
        if user is None:
            raise InvalidTokenError(message="invalid or expired reset token")

        user.password_hash = hash_password(password)
        stored.used_at = datetime.now(tz=UTC)
        await self.refresh_tokens.revoke_all_for_user(user.id)

    async def verify_email(self, token: str) -> None:
        token_hash = self._hash_token(token)
        stored = await self.email_verification_tokens.get_by_hash(token_hash)
        if stored is None or stored.used_at is not None:
            raise InvalidTokenError(message="invalid or expired verification token")
        expires_at = stored.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at <= datetime.now(tz=UTC):
            raise InvalidTokenError(message="invalid or expired verification token")

        user = await self.users.get_by_id(stored.user_id)
        if user is None:
            raise InvalidTokenError(message="invalid or expired verification token")

        user.email_verified = True
        stored.used_at = datetime.now(tz=UTC)

    async def resend_verification(self, user: User) -> ResendVerificationResponse:
        if user.email_verified:
            return ResendVerificationResponse(message="Email is already verified.")
        await self._create_email_verification_token(user)
        return ResendVerificationResponse(
            message="Verification email sent if SMTP is configured.",
        )

    async def _create_email_verification_token(self, user: User) -> None:
        raw_token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(raw_token)
        expires_at = datetime.now(tz=UTC) + timedelta(days=7)
        await self.email_verification_tokens.add(
            EmailVerificationToken(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=expires_at,
            ),
        )
        verify_url = f"{self.settings.frontend_url}/verify-email?token={raw_token}"
        if self.settings.smtp_enabled:
            logger.info("Email verification link for %s: %s", user.email, verify_url)
        else:
            logger.info("Email verification link (dev) for %s: %s", user.email, verify_url)
