"""Distributed simulation API schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SimulationShardResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: UUID
    simulation_id: UUID = Field(alias="simulationId")
    shard_index: int = Field(alias="shardIndex")
    spin_count: int = Field(alias="spinCount")
    status: str
    worker_id: str | None = Field(default=None, alias="workerId")
    started_at: datetime | None = Field(default=None, alias="startedAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")
    error_message: str | None = Field(default=None, alias="errorMessage")


class SimulationShardListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    items: list[SimulationShardResponse]
    total_shards: int = Field(alias="totalShards")
    completed_shards: int = Field(alias="completedShards")
    failed_shards: int = Field(alias="failedShards")
    progress_percentage: float = Field(alias="progressPercentage")


class RetrySimulationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    simulation_id: UUID = Field(alias="simulationId")
    retried_shards: int = Field(alias="retriedShards")


class WorkerStatusItem(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    worker_id: str = Field(alias="workerId")
    status: str
    active_tasks: int = Field(alias="activeTasks")
    processed_tasks: int = Field(alias="processedTasks")


class WorkerListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    active_workers: int = Field(alias="activeWorkers")
    items: list[WorkerStatusItem]


class WorkerHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    healthy: bool
    active_workers: int = Field(alias="activeWorkers")
    checked_at: datetime = Field(alias="checkedAt")


class SimulationQueueResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    pending_tasks: int = Field(alias="pendingTasks")
    running_tasks: int = Field(alias="runningTasks")
    completed_tasks: int = Field(alias="completedTasks")
    failed_tasks: int = Field(alias="failedTasks")
    average_simulation_duration_seconds: float | None = Field(
        default=None,
        alias="averageSimulationDurationSeconds",
    )
