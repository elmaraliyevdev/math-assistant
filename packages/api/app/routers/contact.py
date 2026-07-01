"""Contact form router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user
from app.auth.security_deps import enforce_auth_rate_limit, get_client_ip
from app.config import Settings
from app.dependencies import get_contact_service, get_settings
from app.schemas.contact import (
    ContactSubmissionListResponse,
    ContactSubmissionRequest,
    ContactSubmissionResponse,
)
from app.services.contact_service import ContactService

router = APIRouter(tags=["contact"])


def _is_platform_admin(settings: Settings, email: str) -> bool:
    admins = {
        entry.strip().lower()
        for entry in (settings.platform_admin_emails or "").split(",")
        if entry.strip()
    }
    return email.strip().lower() in admins if admins else False


@router.post(
    "/contact",
    response_model=ContactSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_auth_rate_limit)],
)
async def submit_contact(
    body: ContactSubmissionRequest,
    client_ip: str = Depends(get_client_ip),
    contact_service: ContactService = Depends(get_contact_service),
) -> ContactSubmissionResponse:
    _ = client_ip
    return await contact_service.submit(body)


@router.get(
    "/admin/contact-submissions",
    response_model=ContactSubmissionListResponse,
)
async def list_contact_submissions(
    user=Depends(get_current_user),
    settings: Settings = Depends(get_settings),
    contact_service: ContactService = Depends(get_contact_service),
) -> ContactSubmissionListResponse:
    if not _is_platform_admin(settings, user.email):
        from app.exceptions.domain import ForbiddenError

        raise ForbiddenError(message="platform admin access required")
    return await contact_service.list_submissions()
