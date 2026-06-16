"""Health endpoint tests."""

from __future__ import annotations

import re
from datetime import datetime

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_returns_ok() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z", body["timestamp"])
    parsed = datetime.fromisoformat(body["timestamp"].replace("Z", "+00:00"))
    assert parsed.tzinfo is not None


def test_health_includes_request_id_header() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert "X-Request-Id" in response.headers
    assert response.headers["X-Request-Id"]


def test_health_propagates_request_id() -> None:
    client = TestClient(create_app())
    request_id = "test-request-id-12345"
    response = client.get("/health", headers={"X-Request-Id": request_id})
    assert response.status_code == 200
    assert response.headers["X-Request-Id"] == request_id
