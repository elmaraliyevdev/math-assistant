"""Notification business logic."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import AuthContext
from app.db.models.notification import Notification, NotificationType
from app.db.repositories.notification_repository import NotificationRepository
from app.db.repositories.user_preferences_repository import UserPreferencesRepository
from app.exceptions.domain import NotificationNotFoundError
from app.schemas.platform import (
    MarkAllNotificationsReadResponse,
    MarkNotificationReadResponse,
    NotificationListResponse,
    NotificationResponse,
)


def _to_notification_response(notification: Notification) -> NotificationResponse:
    return NotificationResponse(
        id=notification.id,
        type=notification.type.value,
        title=notification.title,
        message=notification.message,
        organization_id=notification.organization_id,
        entity_type=notification.entity_type,
        entity_id=notification.entity_id,
        read_at=notification.read_at,
        created_at=notification.created_at,
    )


@dataclass(frozen=True, slots=True)
class NotificationService:
    notifications: NotificationRepository
    preferences: UserPreferencesRepository

    @classmethod
    def from_session(cls, session: AsyncSession) -> NotificationService:
        return cls(
            notifications=NotificationRepository(session),
            preferences=UserPreferencesRepository(session),
        )

    async def list_notifications(
        self,
        auth: AuthContext,
        *,
        notification_type: str | None,
        unread_only: bool,
        page: int,
        page_size: int,
    ) -> NotificationListResponse:
        parsed_type = None
        if notification_type is not None:
            parsed_type = NotificationType(notification_type)

        items, total = await self.notifications.list_for_user(
            auth.user_id,
            notification_type=parsed_type,
            unread_only=unread_only,
            page=page,
            page_size=page_size,
        )
        unread_count = await self.notifications.count_unread(auth.user_id)
        return NotificationListResponse(
            items=[_to_notification_response(item) for item in items],
            total=total,
            unread_count=unread_count,
            page=page,
            page_size=page_size,
        )

    async def mark_read(
        self,
        auth: AuthContext,
        notification_id: uuid.UUID,
    ) -> MarkNotificationReadResponse:
        notification = await self.notifications.mark_read(
            notification_id,
            auth.user_id,
        )
        if notification is None:
            raise NotificationNotFoundError(notification_id=str(notification_id))
        return MarkNotificationReadResponse(
            notification_id=notification.id,
            read_at=notification.read_at,  # type: ignore[arg-type]
        )

    async def mark_all_read(self, auth: AuthContext) -> MarkAllNotificationsReadResponse:
        updated = await self.notifications.mark_all_read(auth.user_id)
        return MarkAllNotificationsReadResponse(updated_count=updated)

    async def create_notification(
        self,
        *,
        user_id: uuid.UUID,
        notification_type: NotificationType,
        title: str,
        message: str,
        organization_id: uuid.UUID | None = None,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
    ) -> Notification | None:
        preferences = await self.preferences.get_or_create(user_id)
        if not self._is_enabled(preferences, notification_type):
            return None

        notification = Notification(
            user_id=user_id,
            organization_id=organization_id,
            type=notification_type,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        return await self.notifications.add(notification)

    async def create_collaboration_notification(
        self,
        *,
        user_id: uuid.UUID | None,
        organization_id: uuid.UUID,
        notification_type: str,
        title: str,
        message: str,
        entity_id: uuid.UUID,
    ) -> Notification | None:
        if user_id is None:
            return None
        parsed = NotificationType(notification_type)
        return await self.create_notification(
            user_id=user_id,
            notification_type=parsed,
            title=title,
            message=message,
            organization_id=organization_id,
            entity_type="simulation",
            entity_id=entity_id,
        )

    @staticmethod
    def _is_enabled(preferences, notification_type: NotificationType) -> bool:
        # SQLite + in-memory test setups can occasionally yield unexpected `None`
        # values for boolean preference fields (e.g., when defaults are not applied
        # server-side). Treat `None` as "enabled" to keep user-facing notifications
        # deterministic.
        completed = (
            True
            if preferences.notify_simulation_completed is None
            else preferences.notify_simulation_completed
        )
        failed = (
            True
            if preferences.notify_simulation_failed is None
            else preferences.notify_simulation_failed
        )
        validation_failed = (
            True
            if preferences.notify_validation_failed is None
            else preferences.notify_validation_failed
        )
        org_invitation = (
            True
            if preferences.notify_organization_invitation is None
            else preferences.notify_organization_invitation
        )

        mapping = {
            NotificationType.SIMULATION_COMPLETED: completed,
            NotificationType.SIMULATION_FAILED: failed,
            NotificationType.VALIDATION_FAILED: preferences.notify_validation_failed,
            NotificationType.ORGANIZATION_INVITATION: (
                org_invitation
            ),
            NotificationType.REVIEW_REQUESTED: True,
            NotificationType.CHANGES_REQUESTED: True,
            NotificationType.SIMULATION_APPROVED: True,
            NotificationType.CERTIFICATION_READY: True,
        }
        return mapping.get(notification_type, True)
