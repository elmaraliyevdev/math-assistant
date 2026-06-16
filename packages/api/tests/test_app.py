"""Additional tests for middleware, handlers, and app factory."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Settings
from app.exceptions.handlers import register_exception_handlers
from app.main import create_app
from app.middleware.logging import configure_logging
from app.services.engine_service import EngineService


def test_create_app_with_debug_settings() -> None:
    settings = Settings(debug=True, log_level="DEBUG")
    app = create_app(settings=settings)
    assert app.debug is True


def test_configure_logging_accepts_custom_level() -> None:
    configure_logging(log_level="WARNING")


def test_http_exception_handler_format() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/missing")
    def missing() -> None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Not found")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/missing")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "HTTP_404"
    assert body["error"]["message"] == "Not found"


def test_validation_error_handler_format() -> None:
    app = create_app()
    client = TestClient(app)

    @app.get("/needs-query")
    def needs_query(required: int) -> dict[str, int]:
        return {"required": required}

    response = client.get("/needs-query")
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "INVALID_REQUEST"
    assert body["error"]["message"] == "Request validation failed"
    assert isinstance(body["error"]["details"], list)


def test_engine_service_health_timestamp_format() -> None:
    service = EngineService(settings=Settings())
    health = service.health()
    assert health.status == "ok"
    assert health.timestamp.endswith("Z")


def test_get_settings_requires_app_configuration() -> None:
    from starlette.requests import Request

    from app.dependencies import get_settings

    scope = {"type": "http", "app": FastAPI()}
    request = Request(scope)
    try:
        get_settings(request)
        msg = "expected RuntimeError"
        raise AssertionError(msg)
    except RuntimeError as exc:
        assert "settings not configured" in str(exc)
