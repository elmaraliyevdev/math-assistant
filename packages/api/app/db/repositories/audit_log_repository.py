"""Audit log repository."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import func, select

from app.db.models.audit_log import AuditLog
from app.db.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, session) -> None:
        super().__init__(session, AuditLog)

    async def list_filtered(
        self,
        organization_ids: list[uuid.UUID],
        *,
        user_id: uuid.UUID | None = None,
        action: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        page: int,
        page_size: int,
    ) -> tuple[list[AuditLog], int]:
        query = select(AuditLog).where(
            AuditLog.organization_id.in_(organization_ids),
        )
        count_query = (
            select(func.count())
            .select_from(AuditLog)
            .where(AuditLog.organization_id.in_(organization_ids))
        )

        if user_id is not None:
            query = query.where(AuditLog.user_id == user_id)
            count_query = count_query.where(AuditLog.user_id == user_id)
        if action is not None:
            query = query.where(AuditLog.action == action)
            count_query = count_query.where(AuditLog.action == action)
        if date_from is not None:
            query = query.where(AuditLog.created_at >= date_from)
            count_query = count_query.where(AuditLog.created_at >= date_from)
        if date_to is not None:
            query = query.where(AuditLog.created_at <= date_to)
            count_query = count_query.where(AuditLog.created_at <= date_to)

        total = int(await self._session.scalar(count_query) or 0)
        result = await self._session.scalars(
            query.order_by(AuditLog.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size),
        )
        return list(result.all()), total
