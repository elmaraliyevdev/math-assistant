"""Contact submission ORM model."""

from __future__ import annotations

import enum

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ContactSubmissionType(str, enum.Enum):
    DEMO_REQUEST = "demo_request"
    ENTERPRISE_INQUIRY = "enterprise_inquiry"
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    GENERAL = "general"


class ContactSubmission(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "contact_submissions"

    type: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="new")
