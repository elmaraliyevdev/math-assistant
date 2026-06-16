"""Simulation collaboration workflow enums."""

from __future__ import annotations

import enum


class SimulationWorkflowStatus(enum.StrEnum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    CERTIFICATION_READY = "certification_ready"
    RELEASED = "released"


class ReviewStatus(enum.StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"


class ApprovalStage(enum.StrEnum):
    MATHEMATICIAN = "mathematician"
    SENIOR_MATHEMATICIAN = "senior_mathematician"
    PRODUCT_OWNER = "product_owner"
    PRODUCER = "producer"
