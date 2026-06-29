from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient

pytestmark = pytest.mark.anyio


async def login_and_get_token(app, username: str, password: str) -> str:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": username, "password": password},
        )
    assert response.status_code == 200
    return response.json()["access_token"]


async def test_admin_lists_roles_and_personnel(app, seeded_users) -> None:
    admin_token = await login_and_get_token(app, "admin@test.local", "Admin123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        roles_response = await client.get(
            "/api/v1/personnel/roles",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        personnel_response = await client.get(
            "/api/v1/personnel",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert roles_response.status_code == 200
    assert len(roles_response.json()) == 5
    assert personnel_response.status_code == 200
    assert personnel_response.json()["toplam"] == 5


async def test_driver_cannot_list_personnel(app, seeded_users) -> None:
    driver_token = await login_and_get_token(app, "sofor@test.local", "Sofor123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/api/v1/personnel",
            headers={"Authorization": f"Bearer {driver_token}"},
        )

    assert response.status_code == 403


async def test_finance_can_list_personnel_for_salary(app, seeded_users) -> None:
    finance_token = await login_and_get_token(app, "muhasebe@test.local", "Muhasebe123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/api/v1/personnel",
            headers={"Authorization": f"Bearer {finance_token}"},
        )

    assert response.status_code == 200
    assert response.json()["toplam"] == 5


async def test_admin_creates_and_updates_personnel(app, seeded_users) -> None:
    admin_token = await login_and_get_token(app, "admin@test.local", "Admin123!")
    driver_role_id = seeded_users["driver"].rol_id

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        create_response = await client.post(
            "/api/v1/personnel",
            json={
                "tc_no": "20000000001",
                "ad_soyad": "Yeni Sofor",
                "email": "yeni.sofor@test.local",
                "telefon": "5552000001",
                "taban_maas": "37000.00",
                "cocuk_sayisi": 1,
                "rol_id": driver_role_id,
                "password": "Yeni123!",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        created = create_response.json()

        update_response = await client.patch(
            f"/api/v1/personnel/{created['id']}",
            json={
                "taban_maas": "39000.00",
                "aktif_mi": False,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert create_response.status_code == 201
    assert created["email"] == "yeni.sofor@test.local"
    assert Decimal(update_response.json()["taban_maas"]) == Decimal("39000.00")
    assert update_response.json()["aktif_mi"] is False
