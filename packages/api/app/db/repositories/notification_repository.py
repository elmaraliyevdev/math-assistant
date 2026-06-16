"""Notification repository."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select, update

from app.db.models.notification import Notification, NotificationType
from app.db.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, session) -> None:
        super().__init__(session, Notification)

    async def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        notification_type: NotificationType | None = None,
        unread_only: bool = False,
        page: int,
        page_size: int,
    ) -> tuple[list[Notification], int]:
        query = select(Notification).where(Notification.user_id == user_id)
        count_query = select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id,
        )

        if notification_type is not None:
            query = query.where(Notification.type == notification_type)
            count_query = count_query.where(Notification.type == notification_type)
        if unread_only:
            query = query.where(Notification.read_at.is_(None))
            count_query = count_query.where(Notification.read_at.is_(None))

        total = int(await self._session.scalar(count_query) or 0)
        result = await self._session.scalars(
            query.order_by(Notification.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size),
        )
        return list(result.all()), total

    async def mark_read(
        self,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Notification | None:
        notification = await self.get_by_id(notification_id)
        if notification is None or notification.user_id != user_id:
            return None
        notification.read_at = datetime.now(tz=UTC)
        return await self.save(notification)

    async def mark_all_read(self, user_id: uuid.UUID) -> int:
        now = datetime.now(tz=UTC)
        result = await self._session.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.read_at.is_(None),
            )
            .values(read_at=now),
        )
        return int(result.rowcount or 0)

    async def count_unread(self, user_id: uuid.UUID) -> int:
        count = await self._session.scalar(
            select(func.count())
            .select_from(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.read_at.is_(None),
            ),
        )
        return int(count or 0)
