"""Engine version endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_engine_version_response_schema() -> None:
    client = TestClient(create_app())
    response = client.get("/engine/version")
    assert response.status_code == 200
    body = response.json()
    assert body["engineVersion"] == "runtime-core@1.8.0"
    assert body["validatorVersion"] == "validation-engine@1.0.0"
    assert body["maxRecommendedSpinCount"] == 10_000_000
    assert body["deploymentMode"] == "mvp"
    assert body["maxSimulationSpinCount"] == 10_000_000
    assert body["maxActiveSimulations"] == 2
    assert isinstance(body["activeSimulationCount"], int)
    assert body["rng"] == {"algorithm": "PCG64", "policy": "v1-hash-shard"}

    plugin_ids = {item["pluginId"] for item in body["supportedPlugins"]}
    assert plugin_ids == {
        "core.base-game",
        "core.free-spins",
        "core.hold-and-win",
        "core.multiplier",
    }
    for item in body["supportedPlugins"]:
        assert item["version"] == "1.0.0"


def test_engine_version_respects_settings_override() -> None:
    settings = Settings(max_recommended_spin_count=1_000_000)
    client = TestClient(create_app(settings=settings))
    response = client.get("/engine/version")
    assert response.status_code == 200
    assert response.json()["maxRecommendedSpinCount"] == 1_000_000


def test_engine_version_includes_request_id() -> None:
    client = TestClient(create_app())
    response = client.get("/engine/version", headers={"X-Request-Id": "engine-req-1"})
    assert response.status_code == 200
    assert response.headers["X-Request-Id"] == "engine-req-1"
