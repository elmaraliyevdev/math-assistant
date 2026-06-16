"""Celery application for distributed simulation workers."""

from __future__ import annotations

from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "math_assistant_simulations",
    broker=settings.resolved_celery_broker_url,
    backend=settings.resolved_celery_result_backend,
    include=["app.distributed.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "app.distributed.tasks.run_simulation_shard": {"queue": "simulations"},
        "app.distributed.tasks.orchestrate_simulation": {"queue": "simulations"},
    },
)

if settings.celery_task_always_eager:
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
