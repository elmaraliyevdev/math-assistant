"""Validation API endpoint tests."""

from __future__ import annotations

import copy
import hashlib
import json

from fastapi.testclient import TestClient

from app.adapters.game_version import compute_content_hash
from app.main import create_app


def test_ready_returns_ready_with_engine_version() -> None:
    client = TestClient(create_app())
    response = client.get("/ready")
    assert response.status_code == 200
    body = response.json()
    assert body == {"ready": True, "engineVersion": "runtime-core@1.8.0"}


def test_ready_propagates_request_id() -> None:
    client = TestClient(create_app())
    request_id = "ready-req-abc"
    response = client.get("/ready", headers={"X-Request-Id": request_id})
    assert response.status_code == 200
    assert response.headers["X-Request-Id"] == request_id


def test_validate_success(
    valid_canonical_json: dict,
    expected_content_hash: str,
) -> None:
    client = TestClient(create_app())
    response = client.post(
        "/games/validate",
        json={
            "canonicalJson": valid_canonical_json,
            "engineVersion": "runtime-core@1.8.0",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["contentHash"] == expected_content_hash
    assert body["engineVersion"] == "runtime-core@1.8.0"
    assert body["report"]["passed"] is True
    assert body["report"]["findings"] == []
    assert body["report"]["metadata"]["validatorVersion"] == "validation-engine@1.0.0"
    assert body["report"]["metadata"]["schemaVersion"] == "1.0.0"


def test_validate_failure_returns_422(
    invalid_canonical_json: dict,
    expected_content_hash: str,
) -> None:
    client = TestClient(create_app())
    response = client.post(
        "/games/validate",
        json={
            "canonicalJson": invalid_canonical_json,
            "engineVersion": "runtime-core@1.8.0",
        },
    )
    assert response.status_code == 422
    body = response.json()
    assert body["valid"] is False
    assert body["contentHash"] == compute_content_hash(invalid_canonical_json)
    assert body["contentHash"] != expected_content_hash
    assert body["report"]["passed"] is False
    assert body["report"]["findings"]
    assert "metadata" not in body["report"]
    codes = {finding["code"] for finding in body["report"]["findings"]}
    assert "GV-003" in codes


def test_validate_engine_version_mismatch(valid_canonical_json: dict) -> None:
    client = TestClient(create_app())
    response = client.post(
        "/games/validate",
        json={
            "canonicalJson": valid_canonical_json,
            "engineVersion": "runtime-core@1.0.0",
        },
    )
    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "ENGINE_VERSION_MISMATCH"
    assert body["error"]["details"]["requested"] == "runtime-core@1.0.0"
    assert body["error"]["details"]["deployed"] == "runtime-core@1.8.0"


def test_content_hash_is_deterministic(valid_canonical_json: dict) -> None:
    shuffled = copy.deepcopy(valid_canonical_json)
    reordered = {
        "winModel": shuffled["winModel"],
        "schemaVersion": shuffled["schemaVersion"],
        "metadata": shuffled["metadata"],
        **{
            k: v
            for k, v in shuffled.items()
            if k not in {"winModel", "schemaVersion", "metadata"}
        },
    }
    assert compute_content_hash(valid_canonical_json) == compute_content_hash(reordered)

    payload = json.dumps(
        valid_canonical_json,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    expected = hashlib.sha256(payload).hexdigest()
    assert compute_content_hash(valid_canonical_json) == expected


def test_validate_rejects_invalid_request_body() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/games/validate",
        json={"engineVersion": "runtime-core@1.8.0"},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "INVALID_REQUEST"


def test_validate_rejects_malformed_json_body() -> None:
    client = TestClient(create_app(), raise_server_exceptions=False)
    response = client.post(
        "/games/validate",
        content=b"{not-json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422


def test_validate_rejects_invalid_canonical_json_structure() -> None:
    client = TestClient(create_app(), raise_server_exceptions=False)
    response = client.post(
        "/games/validate",
        json={
            "canonicalJson": {"schemaVersion": "1.0.0"},
            "engineVersion": "runtime-core@1.8.0",
        },
    )
    assert response.status_code == 422
    body = response.json()
    assert body["valid"] is False
    assert body["report"]["passed"] is False
    assert body["report"]["findings"][0]["code"] == "CANONICAL_JSON_INVALID"


def test_validate_propagates_request_id(valid_canonical_json: dict) -> None:
    client = TestClient(create_app())
    request_id = "validate-req-xyz"
    response = client.post(
        "/games/validate",
        json={
            "canonicalJson": valid_canonical_json,
            "engineVersion": "runtime-core@1.8.0",
        },
        headers={"X-Request-Id": request_id},
    )
    assert response.status_code == 200
    assert response.headers["X-Request-Id"] == request_id
