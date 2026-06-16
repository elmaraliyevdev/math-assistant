"""Domain exception handler tests."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.exceptions.domain import (
    DuplicateEmailError,
    DuplicateOrganizationSlugError,
    ForbiddenError,
    GameNotFoundError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
    MemberNotFoundError,
    OrganizationAccessDeniedError,
    OrganizationNotFoundError,
    UnauthorizedError,
    UserNotFoundError,
    ValidationFailedError,
)
from app.exceptions.handlers import register_exception_handlers


def _client_with_route(path: str, exc: Exception) -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)
    client = TestClient(app, raise_server_exceptions=False)

    @app.get(path)
    def raise_error() -> None:
        raise exc

    return client


def test_domain_error_handler_format() -> None:
    response = _client_with_route("/missing-game", GameNotFoundError(game_id="abc")).get(
        "/missing-game",
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "GAME_NOT_FOUND"


def test_validation_failed_handler_format() -> None:
    response = _client_with_route(
        "/invalid",
        ValidationFailedError(content_hash="hash", findings=[]),
    ).get("/invalid")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_FAILED"


def test_auth_related_exception_handlers() -> None:
    cases = [
        (DuplicateEmailError(email="a@b.com"), 409, "DUPLICATE_EMAIL"),
        (InvalidCredentialsError(), 401, "INVALID_CREDENTIALS"),
        (InvalidTokenError(), 401, "INVALID_TOKEN"),
        (InactiveUserError(), 403, "INACTIVE_USER"),
        (UnauthorizedError(), 401, "UNAUTHORIZED"),
    ]
    for exc, status_code, code in cases:
        response = _client_with_route("/error", exc).get("/error")
        assert response.status_code == status_code
        assert response.json()["error"]["code"] == code


def test_organization_exception_handlers() -> None:
    cases = [
        (
            OrganizationNotFoundError(organization_id="org-1"),
            404,
            "ORGANIZATION_NOT_FOUND",
        ),
        (
            OrganizationAccessDeniedError(organization_id="org-1"),
            404,
            "ORGANIZATION_ACCESS_DENIED",
        ),
        (
            DuplicateOrganizationSlugError(slug="studio"),
            409,
            "DUPLICATE_ORGANIZATION_SLUG",
        ),
        (UserNotFoundError(user_id="user-1"), 404, "USER_NOT_FOUND"),
        (
            MemberNotFoundError(user_id="user-1", organization_id="org-1"),
            404,
            "MEMBER_NOT_FOUND",
        ),
        (ForbiddenError(message="nope"), 403, "FORBIDDEN"),
    ]
    for exc, status_code, code in cases:
        response = _client_with_route("/error", exc).get("/error")
        assert response.status_code == status_code
        assert response.json()["error"]["code"] == code
