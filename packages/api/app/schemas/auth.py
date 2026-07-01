"""Authentication API schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(alias="fullName", min_length=1, max_length=255)


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    email: EmailStr
    password: str
    remember_me: bool = Field(default=False, alias="rememberMe")


class RefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    refresh_token: str = Field(alias="refreshToken")


class LogoutRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    refresh_token: str = Field(alias="refreshToken")


class TokenResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    access_token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken")
    token_type: str = Field(default="bearer", alias="tokenType")
    expires_in: int = Field(alias="expiresIn")


class UserResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: UUID
    email: EmailStr
    full_name: str = Field(alias="fullName")
    is_active: bool = Field(alias="isActive")
    email_verified: bool = Field(alias="emailVerified", default=False)
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class RegisterResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    user: UserResponse
    organization_id: UUID = Field(alias="organizationId")
    tokens: TokenResponse


class MeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    user: UserResponse
    organizations: list["OrganizationMembershipResponse"]


class OrganizationMembershipResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    organization_id: UUID = Field(alias="organizationId")
    organization_name: str = Field(alias="organizationName")
    organization_slug: str = Field(alias="organizationSlug")
    role: str


class ForgotPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    message: str


class ResetPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    token: str = Field(min_length=32)
    password: str = Field(min_length=8)


class VerifyEmailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    token: str = Field(min_length=32)


class ResendVerificationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    message: str
