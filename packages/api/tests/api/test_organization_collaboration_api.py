"""Organization invitations and member management API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.api.auth_helpers import auth_headers, register_and_auth, register_user


def test_invite_accept_and_list_members(api_client: TestClient) -> None:
    owner = register_and_auth(api_client, email="owner@example.com")
    invitee = register_user(api_client, email="invitee@example.com")

    invited = api_client.post(
        f"/organizations/{owner['organization_id']}/invitations",
        json={"email": "invitee@example.com", "role": "developer"},
        headers=owner["headers"],
    )
    assert invited.status_code == 201, invited.text
    invitation = invited.json()
    assert invitation["email"] == "invitee@example.com"
    assert invitation["status"] == "pending"

    pending = api_client.get(
        f"/organizations/{owner['organization_id']}/invitations",
        headers=owner["headers"],
    )
    assert pending.status_code == 200
    assert len(pending.json()["items"]) == 1

    mine = api_client.get(
        "/invitations/mine",
        headers=auth_headers(invitee["tokens"]["accessToken"]),
    )
    assert mine.status_code == 200
    assert len(mine.json()["items"]) == 1

    accepted = api_client.post(
        f"/invitations/{invitation['id']}/accept",
        headers=auth_headers(invitee["tokens"]["accessToken"]),
    )
    assert accepted.status_code == 200
    assert accepted.json()["status"] == "accepted"

    members = api_client.get(
        f"/organizations/{owner['organization_id']}/members",
        headers=owner["headers"],
    )
    assert members.status_code == 200
    emails = {item["email"] for item in members.json()["items"]}
    assert emails == {"owner@example.com", "invitee@example.com"}


def test_invitation_requires_matching_email(api_client: TestClient) -> None:
    owner = register_and_auth(api_client, email="owner@example.com")
    other = register_and_auth(api_client, email="other@example.com")

    invited = api_client.post(
        f"/organizations/{owner['organization_id']}/invitations",
        json={"email": "target@example.com", "role": "viewer"},
        headers=owner["headers"],
    ).json()

    response = api_client.post(
        f"/invitations/{invited['id']}/accept",
        headers=other["headers"],
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "INVITATION_EMAIL_MISMATCH"


def test_cancel_pending_invitation(api_client: TestClient) -> None:
    owner = register_and_auth(api_client, email="cancel-owner@example.com")

    invited = api_client.post(
        f"/organizations/{owner['organization_id']}/invitations",
        json={"email": "pending@example.com", "role": "viewer"},
        headers=owner["headers"],
    ).json()

    cancelled = api_client.delete(
        f"/organizations/{owner['organization_id']}/invitations/{invited['id']}",
        headers=owner["headers"],
    )
    assert cancelled.status_code == 204

    pending = api_client.get(
        f"/organizations/{owner['organization_id']}/invitations",
        headers=owner["headers"],
    )
    assert pending.json()["items"] == []


def test_transfer_ownership(api_client: TestClient) -> None:
    owner = register_and_auth(api_client, email="transfer-owner@example.com")
    member = register_user(api_client, email="transfer-member@example.com")

    invitation = api_client.post(
        f"/organizations/{owner['organization_id']}/invitations",
        json={"email": "transfer-member@example.com", "role": "admin"},
        headers=owner["headers"],
    ).json()
    api_client.post(
        f"/invitations/{invitation['id']}/accept",
        headers=auth_headers(member["tokens"]["accessToken"]),
    )

    transferred = api_client.post(
        f"/organizations/{owner['organization_id']}/transfer-ownership",
        json={"newOwnerUserId": member["user"]["id"]},
        headers=owner["headers"],
    )
    assert transferred.status_code == 200
    roles = {
        item["userId"]: item["role"]
        for item in transferred.json()["items"]
    }
    assert roles[owner["user"]["id"]] == "admin"
    assert roles[member["user"]["id"]] == "owner"


def test_expired_invitation_cannot_be_accepted(
    api_client: TestClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    import asyncio
    import uuid
    from datetime import UTC, datetime, timedelta

    from app.db.models.organization_invitation import OrganizationInvitation

    owner = register_and_auth(api_client, email="expire-owner@example.com")

    invited = api_client.post(
        f"/organizations/{owner['organization_id']}/invitations",
        json={"email": "expire-target@example.com", "role": "viewer"},
        headers=owner["headers"],
    ).json()

    async def expire_invitation() -> None:
        async with db_session_factory() as session:
            invitation = await session.get(
                OrganizationInvitation,
                uuid.UUID(invited["id"]),
            )
            assert invitation is not None
            invitation.expires_at = datetime.now(tz=UTC) - timedelta(minutes=1)
            await session.commit()

    asyncio.run(expire_invitation())

    invitee = register_user(api_client, email="expire-target@example.com")
    response = api_client.post(
        f"/invitations/{invited['id']}/accept",
        headers=auth_headers(invitee["tokens"]["accessToken"]),
    )
    assert response.status_code == 410
    assert response.json()["error"]["code"] == "INVITATION_EXPIRED"
