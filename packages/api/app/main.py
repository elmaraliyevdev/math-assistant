"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI

from app.config import Settings, get_settings
from app.db.session import create_engine, create_session_factory
from app.exceptions.handlers import register_exception_handlers
from app.jobs.dispatcher import SimulationDispatcher
from app.jobs.process_pool import SimulationProcessPool
from app.jobs.reload import is_uvicorn_reload_child
from app.jobs.simulation_logging import log_simulation_event, log_simulation_message
from app.middleware.body_size_limit import BodySizeLimitMiddleware
from app.middleware.logging import LoggingMiddleware, configure_logging
from app.middleware.metrics import MetricsMiddleware
from app.middleware.request_id import RequestIdMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.observability.sentry import init_sentry
from app.security.guards import configure_security_guards
from app.routers import (
    audit,
    ai,
    auth,
    dashboard,
    engine,
    exports,
    game_versions,
    games,
    health,
    invitations,
    mathematics,
    metrics,
    notifications,
    organizations,
    settings as settings_router,
    simulations,
    workers,
)
from app.services.validation_service import ValidationService

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


@asynccontextmanager
async def _simulation_lifespan(app: FastAPI) -> AsyncIterator[None]:
    cfg: Settings = app.state.settings
    if cfg.uses_distributed_simulation():
        from app.deployment.redis_check import verify_redis_connectivity
        from app.distributed.queue import DistributedSimulationQueue

        verify_redis_connectivity(cfg.resolved_celery_broker_url)
        app.state.simulation_queue = DistributedSimulationQueue()
        app.state.simulation_dispatcher = None
        app.state.simulation_process_pool = None
        log_simulation_message(
            "Distributed simulation queue ready (Celery)",
            backend=cfg.simulation_execution_backend,
            broker=cfg.resolved_celery_broker_url,
        )
        try:
            yield
        finally:
            app.state.simulation_queue = None
        return

    process_pool = SimulationProcessPool(max_workers=cfg.simulation_process_pool_workers)
    process_pool.start()
    app.state.simulation_process_pool = process_pool
    dispatcher = SimulationDispatcher(
        session_factory=app.state.session_factory,
        process_pool=process_pool,
        settings=cfg,
    )
    await dispatcher.start()
    app.state.simulation_dispatcher = dispatcher
    app.state.simulation_queue = dispatcher.queue
    log_simulation_message(
        "Simulation job queue ready",
        queue_id=id(dispatcher.queue),
        worker_count=len(dispatcher._workers),
        configured_worker_count=cfg.simulation_worker_count,
    )
    if is_uvicorn_reload_child():
        log_simulation_event(
            "simulation_reload_mode_warning",
            message=(
                "uvicorn --reload is enabled; in-memory simulation jobs are lost on "
                "reload and orphaned DB rows are re-enqueued on startup"
            ),
        )
    try:
        yield
    finally:
        await dispatcher.stop()
        app.state.simulation_dispatcher = None
        app.state.simulation_queue = None
        process_pool.shutdown(wait=True)
        app.state.simulation_process_pool = None


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or get_settings()
    configure_logging(log_level=cfg.log_level)
    init_sentry(cfg)
    configure_security_guards(cfg)

    app = FastAPI(
        title=cfg.app_name,
        version="1.0.0",
        debug=cfg.debug,
        lifespan=_simulation_lifespan,
    )
    app.state.settings = cfg
    app.state.validation_service = ValidationService.create()
    db_engine = create_engine(cfg)
    app.state.db_engine = db_engine
    app.state.session_factory = create_session_factory(db_engine)
    register_exception_handlers(app)
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware, settings=cfg)
    app.add_middleware(BodySizeLimitMiddleware, settings=cfg)
    app.add_middleware(RequestIdMiddleware)
    app.include_router(health.router)
    app.include_router(metrics.router)
    app.include_router(engine.router)
    app.include_router(auth.router)
    app.include_router(settings_router.router)
    app.include_router(notifications.router)
    app.include_router(audit.router)
    app.include_router(dashboard.router)
    app.include_router(exports.router)
    app.include_router(organizations.router)
    app.include_router(invitations.router)
    app.include_router(games.router)
    app.include_router(game_versions.router)
    app.include_router(simulations.router)
    app.include_router(workers.router)
    app.include_router(mathematics.router)
    app.include_router(ai.router)
    return app


app = create_app()
