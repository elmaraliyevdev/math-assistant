"""Simulation management router."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.auth.dependencies import get_auth_context
from app.auth.context import AuthContext
from app.dependencies import get_collaboration_service, get_monitoring_service, get_simulation_service
from app.schemas.distributed import (
    RetrySimulationResponse,
    SimulationQueueResponse,
    SimulationShardListResponse,
)
from app.schemas.collaboration import (
    ApproveSimulationRequest,
    CreateSimulationCommentRequest,
    SimulationActivityListResponse,
    SimulationApprovalResponse,
    SimulationCommentListResponse,
    SimulationCommentResponse,
    SimulationReviewResponse,
    SimulationWorkflowResponse,
    SubmitSimulationReviewRequest,
    WorkflowTransitionRequest,
)
from app.schemas.simulations import (
    CancelSimulationResponse,
    CreateSimulationNoteRequest,
    CreateSimulationRequest,
    CreateSimulationResponse,
    SimulationCompareResponse,
    SimulationDetailResponse,
    SimulationListResponse,
    SimulationNoteListResponse,
    SimulationNoteResponse,
    SimulationResultsResponse,
    SimulationThroughputResponse,
)
from app.collaboration.service import CollaborationService
from app.distributed.monitoring_service import MonitoringService
from app.services.simulation_service import SimulationService

router = APIRouter(prefix="/simulations", tags=["simulations"])


def _parse_simulation_ids(raw_ids: str) -> list[uuid.UUID]:
    parts = [part.strip() for part in raw_ids.split(",") if part.strip()]
    return [uuid.UUID(part) for part in parts]


@router.post(
    "",
    response_model=CreateSimulationResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_simulation(
    body: CreateSimulationRequest,
    auth: AuthContext = Depends(get_auth_context),
    simulation_service: SimulationService = Depends(get_simulation_service),
) -> CreateSimulationResponse:
    return await simulation_service.create_simulation(auth, body)


@router.get("/compare", response_model=SimulationCompareResponse)
async def compare_simulations(
    ids: str = Query(..., description="Comma-separated simulation UUIDs"),
    auth: AuthContext = Depends(get_auth_context),
    simulation_service: SimulationService = Depends(get_simulation_service),
) -> SimulationCompareResponse:
    return await simulation_service.compare_simulations(
        auth,
        _parse_simulation_ids(ids),
    )


@router.get("/throughput", response_model=SimulationThroughputResponse)
async def get_simulation_throughput(
    auth: AuthContext = Depends(get_auth_context),
    simulation_service: SimulationService = Depends(get_simulation_service),
) -> SimulationThroughputResponse:
    return await simulation_service.get_throughput(auth)


@router.get("/queue", response_model=SimulationQueueResponse)
async def get_simulation_queue(
    auth: AuthContext = Depends(get_auth_context),
    monitoring: MonitoringService = Depends(get_monitoring_service),
) -> SimulationQueueResponse:
    return await monitoring.queue_summary()


@router.post(
    "/{simulation_id}/cancel",
    response_model=CancelSimulationResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def cancel_simulation(
    simulation_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    simulation_service: SimulationService = Depends(get_simulation_service),
) -> CancelSimulationResponse:
    return await simulation_service.cancel_simulation(auth, simulation_id)


@router.get("", response_model=SimulationListResponse)
async def list_simulations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    status: str | None = Query(default=None),
    game_version_id: uuid.UUID | None = Query(default=None, alias="gameVersionId"),
    auth: AuthContext = Depends(get_auth_context),
    simulation_service: SimulationService = Depends(get_simulation_service),
) -> SimulationListResponse:
    return await simulation_service.list_simulations(
        auth,
        page=page,
        page_size=page_size,
        status=status,
        game_version_id=game_version_id,
    )


@router.get("/{simulation_id}", response_model=SimulationDetailResponse)
async def get_simulation(
    simulation_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    simulation_service: SimulationService = Depends(get_simulation_service),
) -> SimulationDetailResponse:
    return await simulation_service.get_simulation(auth, simulation_id)


@router.get("/{simulation_id}/results", response_model=SimulationResultsResponse)
async def get_simulation_results(
    simulation_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    simulation_service: SimulationService = Depends(get_simulation_service),
) -> SimulationResultsResponse:
    return await simulation_service.get_simulation_results(auth, simulation_id)


@router.get("/{simulation_id}/notes", response_model=SimulationNoteListResponse)
async def list_simulation_notes(
    simulation_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    simulation_service: SimulationService = Depends(get_simulation_service),
) -> SimulationNoteListResponse:
    return await simulation_service.list_simulation_notes(auth, simulation_id)


@router.post(
    "/{simulation_id}/notes",
    response_model=SimulationNoteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_simulation_note(
    simulation_id: uuid.UUID,
    body: CreateSimulationNoteRequest,
    auth: AuthContext = Depends(get_auth_context),
    simulation_service: SimulationService = Depends(get_simulation_service),
) -> SimulationNoteResponse:
    return await simulation_service.create_simulation_note(auth, simulation_id, body)


@router.delete(
    "/{simulation_id}/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_simulation_note(
    simulation_id: uuid.UUID,
    note_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    simulation_service: SimulationService = Depends(get_simulation_service),
) -> None:
    await simulation_service.delete_simulation_note(auth, simulation_id, note_id)


@router.post(
    "/{simulation_id}/review",
    response_model=SimulationReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_simulation_review(
    simulation_id: uuid.UUID,
    body: SubmitSimulationReviewRequest,
    auth: AuthContext = Depends(get_auth_context),
    collaboration_service: CollaborationService = Depends(get_collaboration_service),
) -> SimulationReviewResponse:
    return await collaboration_service.submit_review(auth, simulation_id, body)


@router.get("/{simulation_id}/comments", response_model=SimulationCommentListResponse)
async def list_simulation_comments(
    simulation_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    collaboration_service: CollaborationService = Depends(get_collaboration_service),
) -> SimulationCommentListResponse:
    return await collaboration_service.list_comments(auth, simulation_id)


@router.post(
    "/{simulation_id}/comments",
    response_model=SimulationCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_simulation_comment(
    simulation_id: uuid.UUID,
    body: CreateSimulationCommentRequest,
    auth: AuthContext = Depends(get_auth_context),
    collaboration_service: CollaborationService = Depends(get_collaboration_service),
) -> SimulationCommentResponse:
    return await collaboration_service.add_comment(auth, simulation_id, body)


@router.post(
    "/{simulation_id}/approve",
    response_model=SimulationApprovalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def approve_simulation(
    simulation_id: uuid.UUID,
    body: ApproveSimulationRequest,
    auth: AuthContext = Depends(get_auth_context),
    collaboration_service: CollaborationService = Depends(get_collaboration_service),
) -> SimulationApprovalResponse:
    return await collaboration_service.approve(auth, simulation_id, body)


@router.get("/{simulation_id}/workflow", response_model=SimulationWorkflowResponse)
async def get_simulation_workflow(
    simulation_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    collaboration_service: CollaborationService = Depends(get_collaboration_service),
) -> SimulationWorkflowResponse:
    return await collaboration_service.get_workflow(auth, simulation_id)


@router.get("/{simulation_id}/activity", response_model=SimulationActivityListResponse)
async def list_simulation_activity(
    simulation_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    collaboration_service: CollaborationService = Depends(get_collaboration_service),
) -> SimulationActivityListResponse:
    return await collaboration_service.list_activity(auth, simulation_id)


@router.post(
    "/{simulation_id}/workflow/transition",
    response_model=SimulationWorkflowResponse,
)
async def transition_simulation_workflow(
    simulation_id: uuid.UUID,
    body: WorkflowTransitionRequest,
    auth: AuthContext = Depends(get_auth_context),
    collaboration_service: CollaborationService = Depends(get_collaboration_service),
) -> SimulationWorkflowResponse:
    return await collaboration_service.transition_workflow(auth, simulation_id, body)


@router.get("/{simulation_id}/shards", response_model=SimulationShardListResponse)
async def list_simulation_shards(
    simulation_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    simulation_service: SimulationService = Depends(get_simulation_service),
) -> SimulationShardListResponse:
    return await simulation_service.list_simulation_shards(auth, simulation_id)


@router.post("/{simulation_id}/retry", response_model=RetrySimulationResponse)
async def retry_simulation_shards(
    simulation_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    simulation_service: SimulationService = Depends(get_simulation_service),
) -> RetrySimulationResponse:
    return await simulation_service.retry_failed_shards(auth, simulation_id)
