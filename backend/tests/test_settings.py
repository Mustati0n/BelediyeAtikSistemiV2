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
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    assert response.status_code == 200
    return response.json()["access_token"]


async def test_admin_lists_and_updates_system_parameters(app, seeded_users) -> None:
    admin_token = await login_and_get_token(app, "admin@test.local", "Admin123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        list_response = await client.get(
            "/api/v1/settings/parameters",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        parameter_id = list_response.json()["parametreler"][0]["id"]
        update_response = await client.patch(
            f"/api/v1/settings/parameters/{parameter_id}",
            json={"deger": "90"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert list_response.status_code == 200
    assert list_response.json()["toplam"] >= 9
    assert update_response.status_code == 200
    assert update_response.json()["deger"] == "90"


async def test_driver_cannot_read_system_parameters(app, seeded_users) -> None:
    driver_token = await login_and_get_token(app, "sofor@test.local", "Sofor123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/api/v1/settings/parameters",
            headers={"Authorization": f"Bearer {driver_token}"},
        )

    assert response.status_code == 403
