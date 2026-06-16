"""Notification router."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.auth.dependencies import get_auth_context
from app.auth.context import AuthContext
from app.dependencies import get_notification_service
from app.schemas.platform import (
    MarkAllNotificationsReadResponse,
    MarkNotificationReadResponse,
    NotificationListResponse,
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    type: str | None = Query(default=None, alias="type"),
    unread_only: bool = Query(default=False, alias="unreadOnly"),
    auth: AuthContext = Depends(get_auth_context),
    notification_service: NotificationService = Depends(get_notification_service),
) -> NotificationListResponse:
    return await notification_service.list_notifications(
        auth,
        notification_type=type,
        unread_only=unread_only,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/{notification_id}/read",
    response_model=MarkNotificationReadResponse,
    status_code=status.HTTP_200_OK,
)
async def mark_notification_read(
    notification_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    notification_service: NotificationService = Depends(get_notification_service),
) -> MarkNotificationReadResponse:
    return await notification_service.mark_read(auth, notification_id)


@router.post(
    "/read-all",
    response_model=MarkAllNotificationsReadResponse,
    status_code=status.HTTP_200_OK,
)
async def mark_all_notifications_read(
    auth: AuthContext = Depends(get_auth_context),
    notification_service: NotificationService = Depends(get_notification_service),
) -> MarkAllNotificationsReadResponse:
    return await notification_service.mark_all_read(auth)
