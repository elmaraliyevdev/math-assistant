"""Simulation collaboration API integration tests."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from tests.api.auth_helpers import register_and_auth
from tests.api.test_simulation_notes_api import _completed_simulation


def test_collaboration_workflow_and_comments(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    simulation_id = _completed_simulation(api_client, auth_context, valid_canonical_json)
    headers = auth_context["headers"]

    workflow = api_client.get(f"/simulations/{simulation_id}/workflow", headers=headers)
    assert workflow.status_code == 200
    assert workflow.json()["status"] == "draft"

    comment = api_client.post(
        f"/simulations/{simulation_id}/comments",
        json={"content": "Scatter frequency looks high."},
        headers=headers,
    )
    assert comment.status_code == 201

    comments = api_client.get(
        f"/simulations/{simulation_id}/comments",
        headers=headers,
    )
    assert comments.status_code == 200
    assert len(comments.json()["items"]) == 1

    transition = api_client.post(
        f"/simulations/{simulation_id}/workflow/transition",
        json={"targetStatus": "under_review"},
        headers=headers,
    )
    assert transition.status_code == 200
    assert transition.json()["status"] == "under_review"

    review = api_client.post(
        f"/simulations/{simulation_id}/review",
        json={"status": "approved"},
        headers=headers,
    )
    assert review.status_code == 201
    assert review.json()["status"] == "approved"

    approval = api_client.post(
        f"/simulations/{simulation_id}/approve",
        json={"approvalStage": "mathematician"},
        headers=headers,
    )
    assert approval.status_code == 201

    duplicate = api_client.post(
        f"/simulations/{simulation_id}/approve",
        json={"approvalStage": "mathematician"},
        headers=headers,
    )
    assert duplicate.status_code == 409

    certified = api_client.post(
        f"/simulations/{simulation_id}/workflow/transition",
        json={"targetStatus": "certification_ready"},
        headers=headers,
    )
    assert certified.status_code == 200
    assert certified.json()["status"] == "certification_ready"

    released = api_client.post(
        f"/simulations/{simulation_id}/workflow/transition",
        json={"targetStatus": "released"},
        headers=headers,
    )
    assert released.status_code == 200
    assert released.json()["status"] == "released"

    activity = api_client.get(
        f"/simulations/{simulation_id}/activity",
        headers=headers,
    )
    assert activity.status_code == 200
    assert len(activity.json()["items"]) >= 4


def test_collaboration_permission_denied_for_viewer(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    simulation_id = _completed_simulation(api_client, auth_context, valid_canonical_json)
    viewer = register_and_auth(
        api_client,
        email=f"viewer-{uuid.uuid4()}@example.com",
        full_name="Viewer User",
    )
    org_id = auth_context["organization_id"]
    api_client.post(
        f"/organizations/{org_id}/members",
        json={"userId": viewer["user"]["id"], "role": "viewer"},
        headers=auth_context["headers"],
    )

    response = api_client.post(
        f"/simulations/{simulation_id}/comments",
        json={"content": "Should fail"},
        headers=viewer["headers"],
    )
    assert response.status_code == 403


def test_changes_requested_returns_to_draft(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    simulation_id = _completed_simulation(api_client, auth_context, valid_canonical_json)
    headers = auth_context["headers"]

    api_client.post(
        f"/simulations/{simulation_id}/workflow/transition",
        json={"targetStatus": "under_review"},
        headers=headers,
    )
    review = api_client.post(
        f"/simulations/{simulation_id}/review",
        json={"status": "changes_requested", "decisionReason": "Adjust RTP target"},
        headers=headers,
    )
    assert review.status_code == 201

    workflow = api_client.get(f"/simulations/{simulation_id}/workflow", headers=headers)
    assert workflow.json()["status"] == "draft"


def test_dashboard_includes_collaboration_lists(
    api_client: TestClient,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    simulation_id = _completed_simulation(api_client, auth_context, valid_canonical_json)
    headers = auth_context["headers"]
    api_client.post(
        f"/simulations/{simulation_id}/workflow/transition",
        json={"targetStatus": "under_review"},
        headers=headers,
    )

    summary = api_client.get("/dashboard/summary", headers=headers)
    assert summary.status_code == 200
    body = summary.json()
    assert "pendingReviews" in body
    assert any(item["simulationId"] == simulation_id for item in body["pendingReviews"])
