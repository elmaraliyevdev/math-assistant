"""Organization invitation router."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_auth_context
from app.auth.context import AuthContext
from app.dependencies import get_invitation_service
from app.schemas.organizations import (
    CreateOrganizationInvitationRequest,
    OrganizationInvitationListResponse,
    OrganizationInvitationResponse,
)
from app.services.invitation_service import InvitationService

router = APIRouter(tags=["invitations"])


@router.get("/invitations/mine", response_model=OrganizationInvitationListResponse)
async def list_my_invitations(
    auth: AuthContext = Depends(get_auth_context),
    invitation_service: InvitationService = Depends(get_invitation_service),
) -> OrganizationInvitationListResponse:
    return await invitation_service.list_my_invitations(auth)


@router.post(
    "/invitations/{invitation_id}/accept",
    response_model=OrganizationInvitationResponse,
)
async def accept_invitation(
    invitation_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    invitation_service: InvitationService = Depends(get_invitation_service),
) -> OrganizationInvitationResponse:
    return await invitation_service.accept_invitation(auth, invitation_id)


@router.post(
    "/invitations/{invitation_id}/decline",
    response_model=OrganizationInvitationResponse,
)
async def decline_invitation(
    invitation_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    invitation_service: InvitationService = Depends(get_invitation_service),
) -> OrganizationInvitationResponse:
    return await invitation_service.decline_invitation(auth, invitation_id)
