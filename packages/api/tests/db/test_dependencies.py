"""Dependency wiring tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request

from app.config import Settings
from app.dependencies import (
    get_game_service,
    get_game_version_service,
    get_simulation_service,
)
from app.jobs.dispatcher import SimulationDispatcher
from app.jobs.process_pool import SimulationProcessPool
from app.services.game_service import GameService
from app.services.game_version_service import GameVersionService
from app.services.simulation_service import SimulationService
from app.services.validation_service import ValidationService


@pytest.mark.asyncio
async def test_get_game_service_dependency(db_session: AsyncSession) -> None:
    service = get_game_service(session=db_session)
    assert isinstance(service, GameService)


@pytest.mark.asyncio
async def test_get_game_version_service_dependency(db_engine) -> None:
    app = FastAPI()
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession)
    app.state.session_factory = session_factory
    app.state.validation_service = ValidationService.create()
    request = Request({"type": "http", "app": app})

    async with session_factory() as session:
        service = get_game_version_service(request, session)
        assert isinstance(service, GameVersionService)


@pytest.mark.asyncio
async def test_get_simulation_service_dependency(db_engine) -> None:
    app = FastAPI()
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession)
    app.state.session_factory = session_factory
    settings = Settings(simulation_worker_count=1, simulation_process_pool_workers=1)
    process_pool = SimulationProcessPool(max_workers=1)
    process_pool.start()
    dispatcher = SimulationDispatcher(
        session_factory=session_factory,
        process_pool=process_pool,
        settings=settings,
    )
    app.state.simulation_dispatcher = dispatcher
    request = Request({"type": "http", "app": app})

    async with session_factory() as session:
        service = get_simulation_service(request, session)
        assert isinstance(service, SimulationService)
        assert service.queue is dispatcher.queue

    process_pool.shutdown(wait=True)
