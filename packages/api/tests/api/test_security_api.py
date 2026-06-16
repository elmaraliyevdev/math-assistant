"""Security hardening tests."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.config import Settings
from app.security.guards import configure_security_guards


def _configure_strict_guards(*, rate_limit: int = 3) -> None:
    configure_security_guards(
        Settings(
            rate_limit_auth_per_minute=rate_limit,
            brute_force_max_attempts=2,
            brute_force_lockout_minutes=15,
        ),
    )


def test_security_headers_present(api_client: TestClient) -> None:
    response = api_client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"


def test_oversized_payload_rejected(api_client: TestClient) -> None:
    response = api_client.post(
        "/auth/login",
        content=b"x" * 11_000_000,
        headers={"Content-Type": "application/json", "Content-Length": "11000000"},
    )
    assert response.status_code == 413


def test_auth_rate_limit_enforced(api_client: TestClient) -> None:
    _configure_strict_guards()
    for _ in range(3):
        response = api_client.post(
            "/auth/login",
            json={"email": "nobody@example.com", "password": "wrong-password"},
        )
        assert response.status_code in {401, 429}
    blocked = api_client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "wrong-password"},
    )
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"


def test_brute_force_lockout(api_client: TestClient) -> None:
    _configure_strict_guards(rate_limit=20)
    email = f"brute-{uuid.uuid4().hex[:8]}@example.com"
    registered = api_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "secure-password",
            "fullName": "Brute Force Test",
        },
    )
    assert registered.status_code == 201
    for _ in range(2):
        response = api_client.post(
            "/auth/login",
            json={"email": email, "password": "wrong-password"},
        )
        assert response.status_code == 401
    locked = api_client.post(
        "/auth/login",
        json={"email": email, "password": "wrong-password"},
    )
    assert locked.status_code == 429
    assert locked.json()["error"]["code"] == "ACCOUNT_LOCKED"


def test_refresh_token_rotation(api_client: TestClient, auth_context: dict) -> None:
    login = api_client.post(
        "/auth/login",
        json={
            "email": auth_context["user"]["email"],
            "password": "secure-password",
        },
    )
    assert login.status_code == 200
    original_refresh = login.json()["refreshToken"]
    refreshed = api_client.post(
        "/auth/refresh",
        json={"refreshToken": original_refresh},
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["refreshToken"] != original_refresh

    reuse = api_client.post(
        "/auth/refresh",
        json={"refreshToken": original_refresh},
    )
    assert reuse.status_code == 401


def test_readiness_endpoint(api_client: TestClient) -> None:
    response = api_client.get("/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"ready", "degraded"}
    assert "database" in body["checks"]


def test_metrics_bearer_protection(db_engine) -> None:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from app.dependencies import get_db_session
    from app.main import create_app

    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        jwt_secret_key="test-secret-key",
        metrics_bearer_token="metrics-secret",
    )
    app = create_app(settings=settings)
    configure_security_guards(settings)
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    # Ensure the app lifespan (SimulationDispatcher) uses the same in-memory DB
    # with a pre-created schema; otherwise SQLite's in-memory databases are
    # connection-scoped and the dispatcher can observe a DB without tables.
    app.state.db_engine = db_engine
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
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        denied = client.get("/metrics")
        assert denied.status_code == 401
        allowed = client.get(
            "/metrics",
            headers={"Authorization": "Bearer metrics-secret"},
        )
        assert allowed.status_code == 200
