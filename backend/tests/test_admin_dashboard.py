from datetime import datetime, timezone
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.models.entities import Arac, Bolge, Gorev, IslemLog, Konteyner, Stok
from backend.app.models.enums import AracDurumu, AtikTipi, GorevDurumu, GorevTipi, KonteynerDurumu

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


async def test_admin_dashboard_returns_operational_summary(app, db_session, seeded_users) -> None:
    vehicle = Arac(
        plaka="34ADM001",
        tip="Kompaktor",
        kapasite_kg=12000,
        durum=AracDurumu.AKTIF,
    )
    region = Bolge(ad="Merkez")
    db_session.add_all([vehicle, region])
    db_session.flush()

    container = Konteyner(
        kod="KNT-ADM-001",
        enlem=Decimal("41.0082000"),
        boylam=Decimal("28.9784000"),
        doluluk_orani=92,
        durum=KonteynerDurumu.KRITIK,
        bolge=region,
    )
    task = Gorev(
        tip=GorevTipi.KRITIK_KONTEYNER,
        oncelik=8,
        durum=GorevDurumu.BEKLIYOR,
        planlanan_tarih=datetime.now(timezone.utc),
        konteyner=container,
    )
    stock = Stok(atik_tipi=AtikTipi.PLASTIK, toplam_miktar_kg=Decimal("125.500"))
    log = IslemLog(
        islem_tarihi=datetime.now(timezone.utc),
        islem_tipi="TestIslem",
        aciklama="Dashboard test kaydi",
        varlik_tipi="Gorev",
        varlik_id=1,
        islemi_yapan=seeded_users["admin"],
    )
    db_session.add_all([container, task, stock, log])
    db_session.commit()

    admin_token = await login_and_get_token(app, "admin@test.local", "Admin123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/api/v1/admin/dashboard",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["araclar"]["toplam"] == 1
    assert data["personel"]["toplam"] == 5
    assert data["konteynerler"]["toplam"] == 1
    assert data["gorevler"]["bekleyen"] == 1
    assert data["stok_toplam_kg"] == "125.500"
    assert any(log["islem_tipi"] == "TestIslem" for log in data["son_islemler"])


async def test_non_admin_cannot_read_admin_dashboard(app, seeded_users) -> None:
    driver_token = await login_and_get_token(app, "sofor@test.local", "Sofor123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/api/v1/admin/dashboard",
            headers={"Authorization": f"Bearer {driver_token}"},
        )

    assert response.status_code == 403


async def test_admin_can_filter_audit_logs(app, db_session, seeded_users) -> None:
    db_session.add_all(
        [
            IslemLog(
                islem_tarihi=datetime.now(timezone.utc),
                islem_tipi="GorevAtama",
                aciklama="Kritik konteyner gorevi sofore atandi",
                varlik_tipi="Gorev",
                varlik_id=42,
                islemi_yapan=seeded_users["admin"],
            ),
            IslemLog(
                islem_tarihi=datetime.now(timezone.utc),
                islem_tipi="BakimTamamlama",
                aciklama="Arac bakimi tamamlandi",
                varlik_tipi="BakimKaydi",
                varlik_id=7,
                islemi_yapan=seeded_users["tech"],
            ),
        ]
    )
    db_session.commit()

    admin_token = await login_and_get_token(app, "admin@test.local", "Admin123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/api/v1/admin/logs",
            params={"query": "konteyner", "varlik_tipi": "Gorev", "limit": 10},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["toplam"] == 1
    assert data["loglar"][0]["islem_tipi"] == "GorevAtama"
    assert data["loglar"][0]["yapan"] == seeded_users["admin"].ad_soyad


async def test_admin_audit_logs_support_offset_pagination(app, db_session, seeded_users) -> None:
    for index in range(18):
        db_session.add(
            IslemLog(
                islem_tarihi=datetime.now(timezone.utc),
                islem_tipi=f"SayfalamaTest{index}",
                aciklama=f"Sayfalama test kaydi {index}",
                varlik_tipi="Test",
                varlik_id=index,
                islemi_yapan=seeded_users["admin"],
            )
        )
    db_session.commit()

    admin_token = await login_and_get_token(app, "admin@test.local", "Admin123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        first_page = await client.get(
            "/api/v1/admin/logs",
            params={"query": "Sayfalama", "limit": 15, "offset": 0},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        second_page = await client.get(
            "/api/v1/admin/logs",
            params={"query": "Sayfalama", "limit": 15, "offset": 15},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert first_page.status_code == 200
    assert second_page.status_code == 200
    assert first_page.json()["toplam"] == 18
    assert len(first_page.json()["loglar"]) == 15
    assert len(second_page.json()["loglar"]) == 3


async def test_non_admin_cannot_read_admin_logs(app, seeded_users) -> None:
    driver_token = await login_and_get_token(app, "sofor@test.local", "Sofor123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/api/v1/admin/logs",
            headers={"Authorization": f"Bearer {driver_token}"},
        )

    assert response.status_code == 403
