"""Audit log router."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import get_auth_context
from app.auth.context import AuthContext
from app.dependencies import get_audit_service
from app.schemas.platform import AuditLogListResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    user_id: uuid.UUID | None = Query(default=None, alias="userId"),
    action: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"),
    auth: AuthContext = Depends(get_auth_context),
    audit_service: AuditService = Depends(get_audit_service),
) -> AuditLogListResponse:
    return await audit_service.list_logs(
        auth,
        user_id=user_id,
        action=action,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
