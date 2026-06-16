"""Organization management router."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_auth_context
from app.auth.context import AuthContext
from app.dependencies import get_invitation_service, get_organization_service
from app.schemas.organizations import (
    AddOrganizationMemberRequest,
    CreateOrganizationInvitationRequest,
    CreateOrganizationRequest,
    OrganizationInvitationListResponse,
    OrganizationInvitationResponse,
    OrganizationListResponse,
    OrganizationMemberListResponse,
    OrganizationMemberResponse,
    OrganizationResponse,
    TransferOwnershipRequest,
    UpdateOrganizationRequest,
)
from app.services.invitation_service import InvitationService
from app.services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization(
    body: CreateOrganizationRequest,
    auth: AuthContext = Depends(get_auth_context),
    organization_service: OrganizationService = Depends(get_organization_service),
) -> OrganizationResponse:
    return await organization_service.create_organization(auth, body)


@router.get("", response_model=OrganizationListResponse)
async def list_organizations(
    auth: AuthContext = Depends(get_auth_context),
    organization_service: OrganizationService = Depends(get_organization_service),
) -> OrganizationListResponse:
    return await organization_service.list_organizations(auth)


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    organization_service: OrganizationService = Depends(get_organization_service),
) -> OrganizationResponse:
    return await organization_service.get_organization(auth, organization_id)


@router.patch("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: uuid.UUID,
    body: UpdateOrganizationRequest,
    auth: AuthContext = Depends(get_auth_context),
    organization_service: OrganizationService = Depends(get_organization_service),
) -> OrganizationResponse:
    return await organization_service.update_organization(
        auth,
        organization_id,
        body,
    )


@router.get(
    "/{organization_id}/members",
    response_model=OrganizationMemberListResponse,
)
async def list_organization_members(
    organization_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    organization_service: OrganizationService = Depends(get_organization_service),
) -> OrganizationMemberListResponse:
    return await organization_service.list_members(auth, organization_id)


@router.post(
    "/{organization_id}/members",
    response_model=OrganizationMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_organization_member(
    organization_id: uuid.UUID,
    body: AddOrganizationMemberRequest,
    auth: AuthContext = Depends(get_auth_context),
    organization_service: OrganizationService = Depends(get_organization_service),
) -> OrganizationMemberResponse:
    return await organization_service.add_member(auth, organization_id, body)


@router.delete(
    "/{organization_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_organization_member(
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    organization_service: OrganizationService = Depends(get_organization_service),
) -> None:
    await organization_service.remove_member(auth, organization_id, user_id)


@router.post(
    "/{organization_id}/transfer-ownership",
    response_model=OrganizationMemberListResponse,
)
async def transfer_organization_ownership(
    organization_id: uuid.UUID,
    body: TransferOwnershipRequest,
    auth: AuthContext = Depends(get_auth_context),
    organization_service: OrganizationService = Depends(get_organization_service),
) -> OrganizationMemberListResponse:
    return await organization_service.transfer_ownership(
        auth,
        organization_id,
        body,
    )


@router.post(
    "/{organization_id}/invitations",
    response_model=OrganizationInvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization_invitation(
    organization_id: uuid.UUID,
    body: CreateOrganizationInvitationRequest,
    auth: AuthContext = Depends(get_auth_context),
    invitation_service: InvitationService = Depends(get_invitation_service),
) -> OrganizationInvitationResponse:
    return await invitation_service.create_invitation(
        auth,
        organization_id,
        email=body.email,
        role=body.role,
    )


@router.get(
    "/{organization_id}/invitations",
    response_model=OrganizationInvitationListResponse,
)
async def list_organization_invitations(
    organization_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    invitation_service: InvitationService = Depends(get_invitation_service),
) -> OrganizationInvitationListResponse:
    return await invitation_service.list_organization_invitations(
        auth,
        organization_id,
    )


@router.delete(
    "/{organization_id}/invitations/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def cancel_organization_invitation(
    organization_id: uuid.UUID,
    invitation_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    invitation_service: InvitationService = Depends(get_invitation_service),
) -> None:
    await invitation_service.cancel_invitation(
        auth,
        organization_id,
        invitation_id,
    )
