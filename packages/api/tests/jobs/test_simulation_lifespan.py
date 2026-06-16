"""FastAPI lifespan simulation infrastructure tests."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import Settings
from app.main import create_app


@pytest.mark.asyncio
async def test_lifespan_starts_simulation_dispatcher(db_engine) -> None:
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        simulation_worker_count=1,
        simulation_process_pool_workers=1,
        jwt_secret_key="test-secret-key",
    )
    app = create_app(settings=settings)
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    app.state.session_factory = session_factory

    async with app.router.lifespan_context(app):
        dispatcher = app.state.simulation_dispatcher
        process_pool = app.state.simulation_process_pool
        assert dispatcher is not None
        assert len(dispatcher._workers) == 1
        assert process_pool is not None
        assert process_pool.is_running

    assert not hasattr(app.state, "simulation_dispatcher") or app.state.simulation_dispatcher is None
