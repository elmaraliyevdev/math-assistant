"""Integration tests for simulation job queue lifecycle."""

from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import Settings
from app.dependencies import get_db_session
from app.main import create_app
from tests.api.auth_helpers import register_and_auth


def _wait_for_status(
    client: TestClient,
    simulation_id: str,
    *,
    headers: dict[str, str],
    expected_status: str,
    timeout_seconds: float = 30.0,
) -> dict:
    deadline = time.monotonic() + timeout_seconds
    last_body: dict | None = None
    while time.monotonic() < deadline:
        response = client.get(f"/simulations/{simulation_id}", headers=headers)
        assert response.status_code == 200
        last_body = response.json()
        if last_body["status"] == expected_status:
            return last_body
        time.sleep(0.05)
    msg = f"timed out waiting for {expected_status}, last={last_body}"
    raise AssertionError(msg)


@pytest.fixture
def lifecycle_client(db_engine) -> TestClient:
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

    async def override_db_session():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = override_db_session
    with TestClient(app) as client:
        dispatcher = app.state.simulation_dispatcher
        assert dispatcher is not None
        assert app.state.simulation_queue is dispatcher.queue
        yield client
    app.dependency_overrides.clear()


def test_simulation_transitions_pending_running_completed(
    lifecycle_client: TestClient,
    valid_canonical_json: dict,
) -> None:
    auth = register_and_auth(lifecycle_client)

    game = lifecycle_client.post(
        "/games",
        json={
            "name": "Queue Lifecycle",
            "description": "integration",
            "organizationId": auth["organization_id"],
        },
        headers=auth["headers"],
    )
    assert game.status_code == 201
    game_id = game.json()["id"]

    version = lifecycle_client.post(
        f"/games/{game_id}/versions",
        json={
            "canonicalJson": valid_canonical_json,
            "engineVersion": "runtime-core@1.8.0",
        },
        headers=auth["headers"],
    )
    assert version.status_code == 201
    game_version_id = version.json()["id"]

    dispatcher = lifecycle_client.app.state.simulation_dispatcher
    queue = lifecycle_client.app.state.simulation_queue
    assert queue is dispatcher.queue

    created = lifecycle_client.post(
        "/simulations",
        json={
            "gameVersionId": game_version_id,
            "spinCount": 10,
            "betMinorUnits": 100,
            "eventLogMode": "none",
        },
        headers=auth["headers"],
    )
    assert created.status_code == 202
    simulation_id = created.json()["simulationId"]

    completed = _wait_for_status(
        lifecycle_client,
        simulation_id,
        headers=auth["headers"],
        expected_status="completed",
        timeout_seconds=30.0,
    )
    assert completed["workerId"] is not None
    assert completed["startedAt"] is not None
    assert completed["completedSpinCount"] == 10
    assert completed["progress"]["percentage"] == 100.0
