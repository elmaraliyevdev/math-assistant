"""Game version validation persistence tests."""

from __future__ import annotations


def test_game_version_detail_returns_persisted_validation_summary(
    api_client,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game = api_client.post(
        "/games",
        json={
            "name": "Validation Persist Game",
            "organizationId": auth_context["organization_id"],
        },
        headers=auth_context["headers"],
    )
    assert game.status_code == 201
    game_id = game.json()["id"]
    created = api_client.post(
        f"/games/{game_id}/versions",
        json={
            "canonicalJson": valid_canonical_json,
            "engineVersion": "runtime-core@1.8.0",
        },
        headers=auth_context["headers"],
    )
    assert created.status_code == 201
    version_id = created.json()["id"]

    detail = api_client.get(
        f"/games/{game_id}/versions/{version_id}",
        headers=auth_context["headers"],
    )
    assert detail.status_code == 200
    body = detail.json()
    summary = body["validationSummary"]
    assert summary["passed"] is True
    assert summary["findingCount"] == 0
    assert summary["findings"] == []


def test_create_version_response_includes_findings_array(
    api_client,
    auth_context: dict,
    valid_canonical_json: dict,
) -> None:
    game = api_client.post(
        "/games",
        json={
            "name": "Validation Create Game",
            "organizationId": auth_context["organization_id"],
        },
        headers=auth_context["headers"],
    )
    game_id = game.json()["id"]
    created = api_client.post(
        f"/games/{game_id}/versions",
        json={
            "canonicalJson": valid_canonical_json,
            "engineVersion": "runtime-core@1.8.0",
        },
        headers=auth_context["headers"],
    )
    assert created.status_code == 201
    summary = created.json()["validationSummary"]
    assert "findings" in summary
    assert isinstance(summary["findings"], list)
