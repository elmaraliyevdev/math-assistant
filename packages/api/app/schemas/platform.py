"""Platform API schemas: notifications, audit, settings, dashboard."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.collaboration import CollaborationSimulationSummary


class NotificationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: UUID
    type: str
    title: str
    message: str
    organization_id: UUID | None = Field(default=None, alias="organizationId")
    entity_type: str | None = Field(default=None, alias="entityType")
    entity_id: UUID | None = Field(default=None, alias="entityId")
    read_at: datetime | None = Field(default=None, alias="readAt")
    created_at: datetime = Field(alias="createdAt")


class NotificationListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    items: list[NotificationResponse]
    total: int
    unread_count: int = Field(alias="unreadCount")
    page: int
    page_size: int = Field(alias="pageSize")


class MarkNotificationReadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    notification_id: UUID = Field(alias="notificationId")
    read_at: datetime = Field(alias="readAt")


class MarkAllNotificationsReadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    updated_count: int = Field(alias="updatedCount")


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: UUID
    user_id: UUID | None = Field(default=None, alias="userId")
    user_email: str | None = Field(default=None, alias="userEmail")
    user_name: str | None = Field(default=None, alias="userName")
    organization_id: UUID | None = Field(default=None, alias="organizationId")
    action: str
    entity_type: str = Field(alias="entityType")
    entity_id: UUID | None = Field(default=None, alias="entityId")
    metadata: dict | None = None
    created_at: datetime = Field(alias="createdAt")


class AuditLogListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")


class UserPreferencesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    theme: str
    notify_simulation_completed: bool = Field(alias="notifySimulationCompleted")
    notify_simulation_failed: bool = Field(alias="notifySimulationFailed")
    notify_validation_failed: bool = Field(alias="notifyValidationFailed")
    notify_organization_invitation: bool = Field(alias="notifyOrganizationInvitation")


class UpdateUserPreferencesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    theme: str | None = None
    notify_simulation_completed: bool | None = Field(
        default=None,
        alias="notifySimulationCompleted",
    )
    notify_simulation_failed: bool | None = Field(
        default=None,
        alias="notifySimulationFailed",
    )
    notify_validation_failed: bool | None = Field(
        default=None,
        alias="notifyValidationFailed",
    )
    notify_organization_invitation: bool | None = Field(
        default=None,
        alias="notifyOrganizationInvitation",
    )


class UpdateProfileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    full_name: str | None = Field(default=None, alias="fullName", min_length=1)


class ChangePasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    current_password: str = Field(alias="currentPassword", min_length=8)
    new_password: str = Field(alias="newPassword", min_length=8)


class DashboardRecommendedAction(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    label: str
    description: str
    href: str


class DashboardSimulationSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    simulation_id: UUID = Field(alias="simulationId")
    game_version_id: UUID = Field(alias="gameVersionId")
    game_name: str | None = Field(default=None, alias="gameName")
    game_version_label: str | None = Field(default=None, alias="gameVersionLabel")
    status: str
    workflow_status: str = Field(alias="workflowStatus")
    spin_count: int = Field(alias="spinCount")
    rtp: float | None = None
    within_rtp_tolerance: bool | None = Field(default=None, alias="withinRtpTolerance")
    created_at: datetime = Field(alias="createdAt")


class DashboardSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    total_games: int = Field(alias="totalGames")
    total_simulations: int = Field(alias="totalSimulations")
    active_simulations: int = Field(alias="activeSimulations")
    average_rtp: float | None = Field(default=None, alias="averageRtp")
    recent_notifications: list[NotificationResponse] = Field(
        alias="recentNotifications",
    )
    recent_activity: list[AuditLogResponse] = Field(alias="recentActivity")
    pending_reviews: list[CollaborationSimulationSummary] = Field(
        default_factory=list,
        alias="pendingReviews",
    )
    my_pending_reviews: list[CollaborationSimulationSummary] = Field(
        default_factory=list,
        alias="myPendingReviews",
    )
    certification_ready: list[CollaborationSimulationSummary] = Field(
        default_factory=list,
        alias="certificationReady",
    )
    recently_approved: list[CollaborationSimulationSummary] = Field(
        default_factory=list,
        alias="recentlyApproved",
    )
    recent_simulations: list[DashboardSimulationSummary] = Field(
        default_factory=list,
        alias="recentSimulations",
    )
    outside_rtp_tolerance: list[DashboardSimulationSummary] = Field(
        default_factory=list,
        alias="outsideRtpTolerance",
    )
    recommended_actions: list[DashboardRecommendedAction] = Field(
        default_factory=list,
        alias="recommendedActions",
    )
