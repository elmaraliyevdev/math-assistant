"""Organization API schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.organization_member import OrganizationRole


class CreateOrganizationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class UpdateOrganizationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    name: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: UUID
    name: str
    slug: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class OrganizationListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    items: list[OrganizationResponse]


class AddOrganizationMemberRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    user_id: UUID = Field(alias="userId")
    role: OrganizationRole


class OrganizationMemberResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    user_id: UUID = Field(alias="userId")
    organization_id: UUID = Field(alias="organizationId")
    role: str
    email: str | None = None
    full_name: str | None = Field(default=None, alias="fullName")


class OrganizationMemberListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    items: list[OrganizationMemberResponse]


class TransferOwnershipRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    new_owner_user_id: UUID = Field(alias="newOwnerUserId")


class CreateOrganizationInvitationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    email: str = Field(min_length=3, max_length=320)
    role: OrganizationRole


class OrganizationInvitationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: UUID
    organization_id: UUID = Field(alias="organizationId")
    organization_name: str = Field(alias="organizationName")
    email: str
    role: str
    status: str
    invited_by_user_id: UUID = Field(alias="invitedByUserId")
    expires_at: datetime = Field(alias="expiresAt")
    created_at: datetime = Field(alias="createdAt")
    accepted_at: datetime | None = Field(default=None, alias="acceptedAt")


class OrganizationInvitationListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    items: list[OrganizationInvitationResponse]
