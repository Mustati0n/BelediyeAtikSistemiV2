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


async def test_admin_creates_region_and_container(app, seeded_users) -> None:
    admin_token = await login_and_get_token(app, "admin@test.local", "Admin123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        region_response = await client.post(
            "/api/v1/containers/regions",
            json={"ad": "Merkez", "aciklama": "Ana operasyon bolgesi"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        region = region_response.json()

        create_response = await client.post(
            "/api/v1/containers",
            json={
                "kod": "KNT-001",
                "enlem": "41.0082000",
                "boylam": "28.9784000",
                "doluluk_orani": 76,
                "durum": "Izleniyor",
                "bolge_id": region["id"],
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        list_response = await client.get(
            "/api/v1/containers",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert region_response.status_code == 201
    assert create_response.status_code == 201
    assert create_response.json()["kod"] == "KNT-001"
    assert create_response.json()["bolge"]["ad"] == "Merkez"
    assert list_response.status_code == 200
    assert list_response.json()["toplam"] == 1


async def test_admin_updates_container_status_and_fill(app, seeded_users) -> None:
    admin_token = await login_and_get_token(app, "admin@test.local", "Admin123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        region_response = await client.post(
            "/api/v1/containers/regions",
            json={"ad": "Sahil"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        container_response = await client.post(
            "/api/v1/containers",
            json={
                "kod": "KNT-002",
                "enlem": "40.9900000",
                "boylam": "29.0300000",
                "doluluk_orani": 40,
                "durum": "Normal",
                "bolge_id": region_response.json()["id"],
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        update_response = await client.patch(
            f"/api/v1/containers/{container_response.json()['id']}",
            json={"doluluk_orani": 95, "durum": "Kritik"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert update_response.status_code == 200
    assert update_response.json()["doluluk_orani"] == 95
    assert update_response.json()["durum"] == "Kritik"


async def test_admin_deletes_container_without_open_task(app, seeded_users) -> None:
    admin_token = await login_and_get_token(app, "admin@test.local", "Admin123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        region_response = await client.post(
            "/api/v1/containers/regions",
            json={"ad": "Silinecek Bolge"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        container_response = await client.post(
            "/api/v1/containers",
            json={
                "kod": "DEL-001",
                "enlem": "37.0662000",
                "boylam": "37.3833000",
                "doluluk_orani": 10,
                "durum": "Normal",
                "bolge_id": region_response.json()["id"],
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        delete_response = await client.delete(
            f"/api/v1/containers/{container_response.json()['id']}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        list_response = await client.get(
            "/api/v1/containers",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert delete_response.status_code == 204
    assert all(item["kod"] != "DEL-001" for item in list_response.json()["konteynerler"])


async def test_admin_cannot_delete_container_with_open_task(app, seeded_users) -> None:
    admin_token = await login_and_get_token(app, "admin@test.local", "Admin123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        region_response = await client.post(
            "/api/v1/containers/regions",
            json={"ad": "Gorevli Bolge"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        container_response = await client.post(
            "/api/v1/containers",
            json={
                "kod": "TASK-001",
                "enlem": "37.0662000",
                "boylam": "37.3833000",
                "doluluk_orani": 20,
                "durum": "Normal",
                "bolge_id": region_response.json()["id"],
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        fill_response = await client.post(
            f"/api/v1/operations/konteynerler/{container_response.json()['id']}/doluluk",
            json={"doluluk_orani": 95},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        delete_response = await client.delete(
            f"/api/v1/containers/{container_response.json()['id']}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert fill_response.status_code == 200
    assert fill_response.json()["gorev_olusturuldu"] is True
    assert delete_response.status_code == 409
    assert delete_response.json()["detail"] == "Bu konteynere bagli acik gorev oldugu icin silinemez."


async def test_driver_cannot_list_containers(app, seeded_users) -> None:
    driver_token = await login_and_get_token(app, "sofor@test.local", "Sofor123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/api/v1/containers",
            headers={"Authorization": f"Bearer {driver_token}"},
        )

    assert response.status_code == 403
