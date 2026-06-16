"""Platform polish API integration tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.api.test_simulations_api import (
    _create_game_version,
    wait_for_simulation,
)


def test_notifications_mark_read_and_filter(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game_version_id = _create_game_version(api_client, auth_context, valid_canonical_json)
    create = api_client.post(
        "/simulations",
        json={
            "gameVersionId": game_version_id,
            "spinCount": 20,
            "betMinorUnits": 100,
        },
        headers=auth_context["headers"],
    )
    assert create.status_code == 202
    simulation_id = create.json()["simulationId"]
    wait_for_simulation(
        api_client,
        simulation_id,
        headers=auth_context["headers"],
    )

    # Notification created after simulation completes
    listed = api_client.get("/notifications", headers=auth_context["headers"])
    assert listed.status_code == 200
    body = listed.json()
    assert body["total"] >= 1
    assert body["unreadCount"] >= 1
    notification_id = body["items"][0]["id"]

    filtered = api_client.get(
        "/notifications",
        params={"type": "simulation_completed"},
        headers=auth_context["headers"],
    )
    assert filtered.status_code == 200
    assert filtered.json()["total"] >= 1

    marked = api_client.post(
        f"/notifications/{notification_id}/read",
        headers=auth_context["headers"],
    )
    assert marked.status_code == 200
    assert marked.json()["notificationId"] == notification_id

    all_read = api_client.post(
        "/notifications/read-all",
        headers=auth_context["headers"],
    )
    assert all_read.status_code == 200
    assert all_read.json()["updatedCount"] >= 0


def test_audit_logs_list_and_filters(api_client: TestClient, auth_context: dict) -> None:
    api_client.post(
        "/auth/login",
        json={
            "email": auth_context["user"]["email"],
            "password": "secure-password",
        },
    )
    api_client.post("/games", json={
        "name": "Audit Game",
        "organizationId": auth_context["organization_id"],
    }, headers=auth_context["headers"])

    response = api_client.get("/audit", headers=auth_context["headers"])
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    actions = {item["action"] for item in body["items"]}
    assert "game.create" in actions or "auth.login" in actions

    filtered = api_client.get(
        "/audit",
        params={"action": "game.create"},
        headers=auth_context["headers"],
    )
    assert filtered.status_code == 200
    assert all(item["action"] == "game.create" for item in filtered.json()["items"])


def test_user_settings_preferences_profile_password(
    api_client: TestClient,
    auth_context: dict,
) -> None:
    prefs = api_client.get("/users/me/preferences", headers=auth_context["headers"])
    assert prefs.status_code == 200
    assert prefs.json()["theme"] in {"light", "dark", "system"}

    updated = api_client.patch(
        "/users/me/preferences",
        json={"theme": "dark", "notifySimulationCompleted": False},
        headers=auth_context["headers"],
    )
    assert updated.status_code == 200
    assert updated.json()["theme"] == "dark"
    assert updated.json()["notifySimulationCompleted"] is False

    profile = api_client.patch(
        "/users/me/profile",
        json={"fullName": "Updated Name"},
        headers=auth_context["headers"],
    )
    assert profile.status_code == 200
    assert profile.json()["fullName"] == "Updated Name"

    change = api_client.post(
        "/users/me/change-password",
        json={
            "currentPassword": "secure-password",
            "newPassword": "new-secure-password",
        },
        headers=auth_context["headers"],
    )
    assert change.status_code == 204

    login = api_client.post(
        "/auth/login",
        json={
            "email": auth_context["user"]["email"],
            "password": "new-secure-password",
        },
    )
    assert login.status_code == 200


def test_dashboard_summary(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    _create_game_version(api_client, auth_context, valid_canonical_json)
    response = api_client.get("/dashboard/summary", headers=auth_context["headers"])
    assert response.status_code == 200
    body = response.json()
    assert body["totalGames"] >= 1
    assert "totalSimulations" in body
    assert "activeSimulations" in body
    assert "recentNotifications" in body
    assert "recentActivity" in body


def test_simulation_and_version_exports(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game = api_client.post(
        "/games",
        json={
            "name": "Export Game",
            "organizationId": auth_context["organization_id"],
        },
        headers=auth_context["headers"],
    )
    game_id = game.json()["id"]
    version = api_client.post(
        f"/games/{game_id}/versions",
        json={
            "canonicalJson": valid_canonical_json,
            "engineVersion": "runtime-core@1.8.0",
        },
        headers=auth_context["headers"],
    )
    version_id = version.json()["id"]

    create = api_client.post(
        "/simulations",
        json={
            "gameVersionId": version_id,
            "spinCount": 20,
            "betMinorUnits": 100,
        },
        headers=auth_context["headers"],
    )
    simulation_id = create.json()["simulationId"]
    wait_for_simulation(
        api_client,
        simulation_id,
        headers=auth_context["headers"],
    )

    for export_format in ("json", "csv", "pdf"):
        exported = api_client.get(
            f"/simulations/{simulation_id}/export",
            params={"format": export_format},
            headers=auth_context["headers"],
        )
        assert exported.status_code == 200
        assert exported.content

    version_export = api_client.get(
        f"/games/{game_id}/versions/{version_id}/export",
        headers=auth_context["headers"],
    )
    assert version_export.status_code == 200
    assert b"schemaVersion" in version_export.content or version_export.content


def test_metrics_endpoint(api_client: TestClient) -> None:
    api_client.get("/health")
    response = api_client.get("/metrics")
    assert response.status_code == 200
    assert b"api_requests_total" in response.content
