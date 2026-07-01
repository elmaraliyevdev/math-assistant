"""Contact API schemas."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactType(str, Enum):
    DEMO_REQUEST = "demo_request"
    ENTERPRISE_INQUIRY = "enterprise_inquiry"
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    GENERAL = "general"


class ContactSubmissionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: ContactType
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    company: str | None = Field(default=None, max_length=255)
    message: str = Field(min_length=10, max_length=10_000)


class ContactSubmissionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: UUID


class ContactSubmissionListItem(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: UUID
    type: str
    name: str
    email: EmailStr
    company: str | None
    message: str
    status: str
    created_at: datetime = Field(alias="createdAt")


class ContactSubmissionListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    items: list[ContactSubmissionListItem]
    total: int
