"""Collaboration API schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SimulationCommentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: uuid.UUID
    simulation_id: uuid.UUID = Field(alias="simulationId")
    user_id: uuid.UUID = Field(alias="userId")
    author_name: str | None = Field(default=None, alias="authorName")
    author_email: str | None = Field(default=None, alias="authorEmail")
    author_role: str | None = Field(default=None, alias="authorRole")
    content: str
    created_at: datetime = Field(alias="createdAt")


class SimulationCommentListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    items: list[SimulationCommentResponse]


class CreateSimulationCommentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    content: str = Field(min_length=1)


class SimulationReviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: uuid.UUID
    simulation_id: uuid.UUID = Field(alias="simulationId")
    reviewer_id: uuid.UUID = Field(alias="reviewerId")
    reviewer_name: str | None = Field(default=None, alias="reviewerName")
    reviewer_email: str | None = Field(default=None, alias="reviewerEmail")
    reviewer_role: str | None = Field(default=None, alias="reviewerRole")
    status: str
    decision_reason: str | None = Field(default=None, alias="decisionReason")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class SubmitSimulationReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    status: str
    decision_reason: str | None = Field(default=None, alias="decisionReason")


class SimulationApprovalResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: uuid.UUID
    simulation_id: uuid.UUID = Field(alias="simulationId")
    approved_by: uuid.UUID = Field(alias="approvedBy")
    approval_stage: str = Field(alias="approvalStage")
    approved_at: datetime = Field(alias="approvedAt")


class SimulationApprovalListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    items: list[SimulationApprovalResponse]


class ApproveSimulationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    approval_stage: str = Field(alias="approvalStage")


class SimulationActivityResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: uuid.UUID
    simulation_id: uuid.UUID = Field(alias="simulationId")
    actor_id: uuid.UUID = Field(alias="actorId")
    action: str
    metadata: dict[str, Any] | None = None
    created_at: datetime = Field(alias="createdAt")


class SimulationActivityListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    items: list[SimulationActivityResponse]


class SimulationWorkflowResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    simulation_id: uuid.UUID = Field(alias="simulationId")
    status: str
    reviews: list[SimulationReviewResponse]
    approvals: list[SimulationApprovalResponse]


class WorkflowTransitionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    target_status: str = Field(alias="targetStatus")


class CollaborationSimulationSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    simulation_id: uuid.UUID = Field(alias="simulationId")
    workflow_status: str = Field(alias="workflowStatus")
    game_version_id: uuid.UUID = Field(alias="gameVersionId")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")
