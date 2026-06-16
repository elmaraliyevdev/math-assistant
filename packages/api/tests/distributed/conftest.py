"""Distributed simulation test fixtures."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.config import Settings
from app.db.base import Base
from app.dependencies import get_db_session
from app.distributed.celery_app import celery_app
from app.main import create_app
from app.security.guards import configure_security_guards


@pytest_asyncio.fixture
async def db_engine() -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
def distributed_api_client(db_engine: AsyncEngine) -> Iterator[TestClient]:
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        simulation_worker_count=1,
        jwt_secret_key="test-secret-key",
        simulation_execution_backend="distributed",
        celery_task_always_eager=True,
    )
    configure_security_guards(settings)
    app = create_app(settings=settings)
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    app.state.session_factory = session_factory

    async def override_db_session():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = override_db_session
    import app.distributed.tasks as distributed_tasks

    distributed_tasks._test_session_factory = session_factory
    try:
        with TestClient(app) as client:
            yield client
    finally:
        distributed_tasks._test_session_factory = None
    app.dependency_overrides.clear()
    celery_app.conf.task_always_eager = False
