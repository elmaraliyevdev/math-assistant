"""Audit logging service."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import AuthContext
from app.db.models.audit_log import AuditLog
from app.db.repositories.audit_log_repository import AuditLogRepository
from app.db.repositories.user_repository import UserRepository
from app.schemas.platform import AuditLogListResponse, AuditLogResponse


def _to_audit_response(log: AuditLog, user_email: str | None, user_name: str | None) -> AuditLogResponse:
    return AuditLogResponse(
        id=log.id,
        user_id=log.user_id,
        user_email=user_email,
        user_name=user_name,
        organization_id=log.organization_id,
        action=log.action,
        entity_type=log.entity_type,
        entity_id=log.entity_id,
        metadata=log.details,
        created_at=log.created_at,
    )


@dataclass(frozen=True, slots=True)
class AuditService:
    audit_logs: AuditLogRepository
    users: UserRepository

    @classmethod
    def from_session(cls, session: AsyncSession) -> AuditService:
        return cls(
            audit_logs=AuditLogRepository(session),
            users=UserRepository(session),
        )

    async def record(
        self,
        *,
        action: str,
        entity_type: str,
        entity_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        organization_id: uuid.UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            organization_id=organization_id,
            details=metadata,
        )
        return await self.audit_logs.add(entry)

    async def list_logs(
        self,
        auth: AuthContext,
        *,
        user_id: uuid.UUID | None,
        action: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
        page: int,
        page_size: int,
    ) -> AuditLogListResponse:
        items, total = await self.audit_logs.list_filtered(
            auth.organization_ids,
            user_id=user_id,
            action=action,
            date_from=date_from,
            date_to=date_to,
            page=page,
            page_size=page_size,
        )

        user_cache: dict[uuid.UUID, tuple[str | None, str | None]] = {}
        responses: list[AuditLogResponse] = []
        for item in items:
            email: str | None = None
            name: str | None = None
            if item.user_id is not None:
                if item.user_id not in user_cache:
                    user = await self.users.get_by_id(item.user_id)
                    user_cache[item.user_id] = (
                        user.email if user else None,
                        user.full_name if user else None,
                    )
                email, name = user_cache[item.user_id]
            responses.append(_to_audit_response(item, email, name))

        return AuditLogListResponse(
            items=responses,
            total=total,
            page=page,
            page_size=page_size,
        )
