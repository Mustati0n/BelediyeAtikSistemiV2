import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.security import safe_verify_token
from backend.app.models.entities import IslemLog

pytestmark = pytest.mark.anyio

async def test_login_returns_bearer_token(app, seeded_users) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": "admin@test.local", "password": "Admin123!"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    token_payload = safe_verify_token(payload["access_token"])
    assert token_payload is not None
    assert token_payload["email"] == "admin@test.local"
    assert token_payload["role"] == "Sistem Yoneticisi"


async def test_me_endpoint_returns_current_user(app, seeded_users) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": "admin@test.local", "password": "Admin123!"},
        )
        token = login_response.json()["access_token"]

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert response.json()["rol"] == "Sistem Yoneticisi"


async def test_admin_check_forbids_non_admin(app, seeded_users) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": "sofor@test.local", "password": "Sofor123!"},
        )
        token = login_response.json()["access_token"]

        response = await client.get(
            "/api/v1/auth/admin-check",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 403


async def test_login_writes_audit_log(app, seeded_users, db_session: Session) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": "10000000001", "password": "Admin123!"},
        )

    assert response.status_code == 200
    logs = db_session.scalars(select(IslemLog)).all()
    assert len(logs) == 1
    assert logs[0].islem_tipi == "Login"
