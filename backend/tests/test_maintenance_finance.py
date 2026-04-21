from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.entities import GiderKaydi, IslemLog, MaasOdeme
from backend.app.models.enums import AracDurumu, BakimDurumu, OdemeTipi, OnayDurumu

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


async def test_vehicle_create_and_update_flow(app, db_session: Session, seeded_users) -> None:
    admin_token = await login_and_get_token(app, "admin@test.local", "Admin123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        create_response = await client.post(
            "/api/v1/fleet/araclar",
            json={"plaka": "06XYZ123", "tip": "Vakumlu Arac", "kapasite_kg": 7000},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        arac_id = create_response.json()["id"]
        update_response = await client.patch(
            f"/api/v1/fleet/araclar/{arac_id}",
            json={"durum": AracDurumu.PASIF.value},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert create_response.status_code == 201
    assert update_response.status_code == 200
    assert update_response.json()["durum"] == AracDurumu.PASIF.value


async def test_maintenance_creation_generates_pending_expense(
    app,
    db_session: Session,
    seeded_users,
) -> None:
    admin_token = await login_and_get_token(app, "admin@test.local", "Admin123!")
    tech_token = await login_and_get_token(app, "bakim@test.local", "Bakim123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        vehicle_response = await client.post(
            "/api/v1/fleet/araclar",
            json={"plaka": "34BAK123", "tip": "Cop Kamyonu", "kapasite_kg": 8000},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        arac_id = vehicle_response.json()["id"]
        bakim_response = await client.post(
            "/api/v1/maintenance/bakim-kayitlari",
            json={
                "arac_id": arac_id,
                "aciklama": "Motor bakimi gerekli.",
                "maliyet_tl": "12500.00",
            },
            headers={"Authorization": f"Bearer {tech_token}"},
        )

    assert bakim_response.status_code == 200
    payload = bakim_response.json()
    assert payload["durum"] == BakimDurumu.ACILDI.value
    assert payload["arac_durumu"] == AracDurumu.BAKIMDA.value
    assert payload["gider_durumu"] == OnayDurumu.BEKLEMEDE.value

    gider = db_session.scalar(select(GiderKaydi))
    assert gider is not None
    assert gider.tutar == Decimal("12500.00")


async def test_technical_completion_and_expense_approval_are_separate(
    app,
    db_session: Session,
    seeded_users,
) -> None:
    admin_token = await login_and_get_token(app, "admin@test.local", "Admin123!")
    tech_token = await login_and_get_token(app, "bakim@test.local", "Bakim123!")
    finance_token = await login_and_get_token(app, "muhasebe@test.local", "Muhasebe123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        vehicle_response = await client.post(
            "/api/v1/fleet/araclar",
            json={"plaka": "06FIN456", "tip": "Bakim Araci", "kapasite_kg": 5000},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        bakim_response = await client.post(
            "/api/v1/maintenance/bakim-kayitlari",
            json={
                "arac_id": vehicle_response.json()["id"],
                "aciklama": "Fren degisimi.",
                "maliyet_tl": "8000.00",
            },
            headers={"Authorization": f"Bearer {tech_token}"},
        )
        bakim_id = bakim_response.json()["id"]
        gider_id = bakim_response.json()["gider_kaydi_id"]

        teknik_complete = await client.post(
            f"/api/v1/maintenance/bakim-kayitlari/{bakim_id}/teknik-tamamla",
            headers={"Authorization": f"Bearer {tech_token}"},
        )
        approve_response = await client.post(
            f"/api/v1/finance/giderler/{gider_id}/onayla",
            headers={"Authorization": f"Bearer {finance_token}"},
        )

    assert teknik_complete.status_code == 200
    assert teknik_complete.json()["durum"] == BakimDurumu.TAMAMLANDI.value
    assert teknik_complete.json()["arac_durumu"] == AracDurumu.AKTIF.value
    assert approve_response.status_code == 200
    assert approve_response.json()["durum"] == OnayDurumu.ONAYLANDI.value


async def test_salary_calculation_single_and_batch_payment(
    app,
    db_session: Session,
    seeded_users,
) -> None:
    finance_token = await login_and_get_token(app, "muhasebe@test.local", "Muhasebe123!")
    finance_user = seeded_users["finance"]
    tech_user = seeded_users["tech"]

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        calc_response = await client.get(
            f"/api/v1/finance/maas/personeller/{finance_user.id}/hesapla",
            headers={"Authorization": f"Bearer {finance_token}"},
        )
        single_response = await client.post(
            "/api/v1/finance/maas/tekli",
            json={
                "personel_id": tech_user.id,
                "donem_ay": 4,
                "donem_yil": 2026,
                "odeme_tarihi": "2026-04-10",
                "tutar": "2500.00",
                "odeme_tipi": OdemeTipi.AVANS.value,
            },
            headers={"Authorization": f"Bearer {finance_token}"},
        )
        batch_response = await client.post(
            "/api/v1/finance/maas/toplu",
            json={"donem_ay": 4, "donem_yil": 2026, "odeme_tarihi": "2026-04-15"},
            headers={"Authorization": f"Bearer {finance_token}"},
        )

    assert calc_response.status_code == 200
    assert calc_response.json()["toplam_hesaplanan_maas"] == "43000.00"
    assert single_response.status_code == 200
    assert single_response.json()["odeme_tipi"] == OdemeTipi.AVANS.value
    assert batch_response.status_code == 200
    assert batch_response.json()["kayit_sayisi"] == 4

    odemeler = list(db_session.scalars(select(MaasOdeme)))
    assert len(odemeler) == 5


async def test_profit_loss_summary_and_pending_expense_listing(
    app,
    db_session: Session,
    seeded_users,
) -> None:
    admin_token = await login_and_get_token(app, "admin@test.local", "Admin123!")
    tech_token = await login_and_get_token(app, "bakim@test.local", "Bakim123!")
    finance_token = await login_and_get_token(app, "muhasebe@test.local", "Muhasebe123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        vehicle_response = await client.post(
            "/api/v1/fleet/araclar",
            json={"plaka": "35RPR789", "tip": "Toplama Araci", "kapasite_kg": 9000},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        await client.post(
            "/api/v1/maintenance/bakim-kayitlari",
            json={
                "arac_id": vehicle_response.json()["id"],
                "aciklama": "Rutin kontrol.",
                "maliyet_tl": "3000.00",
            },
            headers={"Authorization": f"Bearer {tech_token}"},
        )
        pending_response = await client.get(
            "/api/v1/finance/giderler/bekleyen",
            headers={"Authorization": f"Bearer {finance_token}"},
        )
        summary_response = await client.get(
            "/api/v1/finance/raporlar/kar-zarar",
            headers={"Authorization": f"Bearer {finance_token}"},
        )

    assert pending_response.status_code == 200
    assert len(pending_response.json()) == 1
    assert summary_response.status_code == 200
    assert summary_response.json()["bekleyen_gider_sayisi"] == 1

    logs = list(db_session.scalars(select(IslemLog)))
    assert len(logs) >= 4
