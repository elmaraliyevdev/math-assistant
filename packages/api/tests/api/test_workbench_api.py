"""Mathematician workbench API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.api.auth_helpers import register_and_auth


def test_simulation_throughput_endpoint(api_client: TestClient) -> None:
    auth = register_and_auth(api_client, email="throughput@example.com")
    response = api_client.get("/simulations/throughput", headers=auth["headers"])
    assert response.status_code == 200
    body = response.json()
    assert body["spinsPerSecond"] > 0
    assert body["source"] in {"historical", "deployment_fallback"}


def test_dashboard_includes_workbench_fields(
    api_client: TestClient,
    auth_context: dict,
) -> None:
    response = api_client.get("/dashboard/summary", headers=auth_context["headers"])
    assert response.status_code == 200
    body = response.json()
    assert "recentSimulations" in body
    assert "outsideRtpTolerance" in body
    assert "recommendedActions" in body
    assert "myPendingReviews" in body
    assert isinstance(body["recommendedActions"], list)
    assert isinstance(body["myPendingReviews"], list)


def test_review_requires_decision_reason(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    from tests.api.test_simulation_notes_api import _completed_simulation

    simulation_id = _completed_simulation(api_client, auth_context, valid_canonical_json)
    headers = auth_context["headers"]
    api_client.post(
        f"/simulations/{simulation_id}/workflow/transition",
        json={"targetStatus": "under_review"},
        headers=headers,
    )
    response = api_client.post(
        f"/simulations/{simulation_id}/review",
        json={"status": "rejected"},
        headers=headers,
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "REVIEW_DECISION_REQUIRED"
