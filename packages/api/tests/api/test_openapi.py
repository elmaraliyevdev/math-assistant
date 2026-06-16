"""OpenAPI schema tests."""

from __future__ import annotations

from app.main import create_app


def test_openapi_includes_game_management_paths() -> None:
    schema = create_app().openapi()
    paths = schema["paths"]

    assert "/games" in paths
    assert "post" in paths["/games"]
    assert "get" in paths["/games"]
    assert "/games/{game_id}" in paths
    assert "patch" in paths["/games/{game_id}"]
    assert "delete" in paths["/games/{game_id}"]
    assert "/games/{game_id}/versions" in paths
    assert "post" in paths["/games/{game_id}/versions"]
    assert "/games/{game_id}/versions/{version_id}" in paths
    assert "/simulations" in paths
    assert "post" in paths["/simulations"]
    assert "/simulations/{simulation_id}/results" in paths


def test_openapi_create_game_request_has_example() -> None:
    schema = create_app().openapi()
    create_schema = schema["components"]["schemas"]["CreateGameRequest"]
    assert "examples" in create_schema
    assert create_schema["examples"][0]["name"] == "Book of Fortune"


def test_openapi_create_version_request_has_example() -> None:
    schema = create_app().openapi()
    create_schema = schema["components"]["schemas"]["CreateGameVersionRequest"]
    assert "examples" in create_schema
    assert create_schema["examples"][0]["engineVersion"] == "runtime-core@1.8.0"


def test_openapi_create_simulation_request_has_example() -> None:
    schema = create_app().openapi()
    create_schema = schema["components"]["schemas"]["CreateSimulationRequest"]
    assert "examples" in create_schema
    assert create_schema["examples"][0]["spinCount"] == 1000
