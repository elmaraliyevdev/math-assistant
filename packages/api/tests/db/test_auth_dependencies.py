"""Authentication dependency tests."""

from __future__ import annotations

import uuid

import pytest
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.testclient import TestClient

from app.auth.context import AuthContext
from app.auth.dependencies import get_auth_context, get_current_user, require_role
from app.config import Settings
from app.db.models.organization_member import OrganizationRole
from app.exceptions.domain import InactiveUserError, UnauthorizedError
from app.exceptions.handlers import register_exception_handlers
from app.security.jwt import create_access_token


@pytest.mark.asyncio
async def test_get_current_user_missing_token(db_session: AsyncSession) -> None:
    with pytest.raises(UnauthorizedError):
        await get_current_user(token=None, session=db_session, settings=Settings())


@pytest.mark.asyncio
async def test_get_current_user_inactive(
    db_session: AsyncSession,
    user_repo,
    sample_user,
) -> None:
    sample_user.is_active = False
    await user_repo.add(sample_user)
    settings = Settings(jwt_secret_key="test-secret-key")
    token = create_access_token(
        settings=settings,
        user_id=sample_user.id,
        email=sample_user.email,
    )
    with pytest.raises(InactiveUserError):
        await get_current_user(token=token, session=db_session, settings=settings)


@pytest.mark.asyncio
async def test_get_auth_context_builds_memberships(
    db_session: AsyncSession,
    auth_context: AuthContext,
) -> None:
    context = await get_auth_context(user=auth_context.user, session=db_session)
    assert auth_context.organization_ids[0] in context.organization_ids


def test_require_role_dependency_enforces_minimum_role(
    db_engine,
    auth_context: AuthContext,
) -> None:
    app = FastAPI()
    register_exception_handlers(app)
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession)
    app.state.session_factory = session_factory
    org_id = auth_context.organization_ids[0]

    @app.get("/protected")
    async def protected(
        organization_id: uuid.UUID,
        auth: AuthContext = Depends(require_role(OrganizationRole.OWNER)),
    ) -> dict[str, str]:
        return {"organizationId": str(organization_id)}

    app.dependency_overrides[get_auth_context] = lambda: auth_context

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/protected", params={"organization_id": str(org_id)})
    assert response.status_code == 200

    viewer_context = AuthContext(
        user=auth_context.user,
        memberships={org_id: OrganizationRole.VIEWER},
    )
    app.dependency_overrides[get_auth_context] = lambda: viewer_context
    denied = client.get("/protected", params={"organization_id": str(org_id)})
    assert denied.status_code == 403

    app.dependency_overrides.clear()
