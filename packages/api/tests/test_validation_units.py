"""Unit tests for validation adapters and service."""

from __future__ import annotations

import copy

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from runtime_core.validation import ValidationReport
from starlette.requests import Request

from app.adapters.game_version import compute_content_hash, parse_game_version
from app.exceptions.engine import EngineVersionMismatchError
from app.exceptions.handlers import register_exception_handlers
from app.main import create_app
from app.services.validation_service import (
    ValidationService,
    _schema_version,
    _to_api_report,
)


def test_parse_game_version_round_trip(valid_canonical_json: dict) -> None:
    game = parse_game_version(valid_canonical_json)
    assert game.schema_version == "1.0.0"


def test_schema_version_defaults_when_missing() -> None:
    assert _schema_version({}) == "1.0.0"


def test_schema_version_reads_canonical_field() -> None:
    assert _schema_version({"schemaVersion": "2.0.0"}) == "2.0.0"


def test_to_api_report_omits_metadata_when_disabled() -> None:
    report = ValidationReport.empty(content_hash="abc")
    api_report = _to_api_report(report, schema_version="1.0.0", include_metadata=False)
    assert api_report.metadata is None


def test_validation_service_raises_on_engine_mismatch(
    valid_canonical_json: dict,
) -> None:
    service = ValidationService.create()
    with pytest.raises(EngineVersionMismatchError) as exc_info:
        service.validate(
            canonical_json=valid_canonical_json,
            engine_version="runtime-core@9.9.9",
        )
    assert exc_info.value.requested == "runtime-core@9.9.9"
    assert exc_info.value.deployed == "runtime-core@1.8.0"


def test_engine_version_mismatch_handler_format() -> None:
    app = FastAPI()
    register_exception_handlers(app)
    client = TestClient(app, raise_server_exceptions=False)

    @app.get("/boom")
    def boom() -> None:
        raise EngineVersionMismatchError(
            requested="runtime-core@1.0.0",
            deployed="runtime-core@1.8.0",
        )

    response = client.get("/boom")
    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "ENGINE_VERSION_MISMATCH"


def test_get_validation_service_requires_app_configuration() -> None:
    from app.dependencies import get_validation_service

    scope = {"type": "http", "app": FastAPI()}
    request = Request(scope)
    with pytest.raises(RuntimeError, match="validation service not configured"):
        get_validation_service(request)


def test_create_app_configures_validation_service() -> None:
    app = create_app()
    assert isinstance(app.state.validation_service, ValidationService)
    assert app.state.session_factory is not None


def test_compute_content_hash_changes_when_payload_changes(
    valid_canonical_json: dict,
) -> None:
    modified = copy.deepcopy(valid_canonical_json)
    modified["metadata"]["title"] = "Changed Title"
    assert compute_content_hash(valid_canonical_json) != compute_content_hash(modified)
