from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.entities import Arac, Bolge, Gorev, IslemLog, Konteyner
from backend.app.models.enums import (
    AracDurumu,
    GorevDurumu,
    GorevSonucu,
    GorevTipi,
    IhbarDurumu,
    KonteynerDurumu,
)

pytestmark = pytest.mark.anyio


@pytest.fixture()
def operations_data(db_session: Session, seeded_users):
    bolge = Bolge(ad="Merkez", aciklama="Merkez bolgesi")
    konteyner = Konteyner(
        kod="KNT-001",
        enlem=Decimal("39.9207700"),
        boylam=Decimal("32.8541100"),
        doluluk_orani=40,
        durum=KonteynerDurumu.NORMAL,
        bolge=bolge,
    )
    arac = Arac(
        plaka="06ABC123",
        tip="Cop Kamyonu",
        kapasite_kg=8000,
        durum=AracDurumu.AKTIF,
    )
    db_session.add_all([bolge, konteyner, arac])
    db_session.commit()
    db_session.refresh(konteyner)
    db_session.refresh(arac)
    return {"konteyner": konteyner, "arac": arac, **seeded_users}


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


async def test_public_report_creates_ihbar_and_task(app) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/v1/public/ihbarlar",
            json={
                "aciklama": "Konteyner tasiyor ve cevreye cop dokuluyor.",
                "enlem": "37.0667000",
                "boylam": "37.3835000",
            },
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["durum"] == IhbarDurumu.GOREVE_ATANDI.value
    assert payload["ihbar_id"] > 0
    assert payload["gorev_id"] > 0


async def test_public_report_status_can_be_queried(app) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        create_response = await client.post(
            "/api/v1/public/ihbarlar",
            json={
                "aciklama": "Durum sorgusu icin test ihbari.",
                "enlem": "37.0667000",
                "boylam": "37.3835000",
            },
        )
        status_response = await client.get(
            f"/api/v1/public/ihbarlar/{create_response.json()['ihbar_id']}"
        )

    assert status_response.status_code == 200
    payload = status_response.json()
    assert payload["durum"] == IhbarDurumu.GOREVE_ATANDI.value
    assert payload["gorev_id"] == create_response.json()["gorev_id"]


async def test_public_report_photo_can_be_uploaded_and_served(app) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        upload_response = await client.post(
            "/api/v1/public/ihbarlar/fotograf",
            files={"file": ("ihbar.png", b"test-image-bytes", "image/png")},
        )

        assert upload_response.status_code == 200
        payload = upload_response.json()
        assert payload["fotograf_url"].startswith("/api/v1/public/uploads/ihbar/")
        assert payload["dosya_adi"] == "ihbar.png"
        assert payload["boyut"] == len(b"test-image-bytes")

        read_response = await client.get(payload["fotograf_url"])

    assert read_response.status_code == 200
    assert read_response.content == b"test-image-bytes"

    uploaded_file = Path("uploads/ihbar") / Path(payload["fotograf_url"]).name
    if uploaded_file.exists():
        uploaded_file.unlink()


async def test_operator_creates_report_task_from_map(app, db_session: Session, seeded_users) -> None:
    operator_token = await login_and_get_token(app, "operator@test.local", "Operator123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/v1/operations/ihbarlar",
            json={
                "aciklama": "Haritadan secilen okul bolgesinde atik birikmesi var.",
                "enlem": "37.0667000",
                "boylam": "37.3835000",
            },
            headers={"Authorization": f"Bearer {operator_token}"},
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["durum"] == IhbarDurumu.GOREVE_ATANDI.value
    assert payload["gorev_id"] > 0
    assert (
        db_session.scalar(
            select(IslemLog).where(
                IslemLog.varlik_tipi == "Gorev",
                IslemLog.varlik_id == payload["gorev_id"],
                IslemLog.islem_tipi == "GorevOlusturma",
            )
        )
        is not None
    )


async def test_driver_cannot_create_report_task_from_map(app, seeded_users) -> None:
    driver_token = await login_and_get_token(app, "sofor@test.local", "Sofor123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/v1/operations/ihbarlar",
            json={
                "aciklama": "Yetkisiz gorev olusturma denemesi.",
                "enlem": "37.0667000",
                "boylam": "37.3835000",
            },
            headers={"Authorization": f"Bearer {driver_token}"},
        )

    assert response.status_code == 403


async def test_public_report_outside_gaziantep_is_rejected(app) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/v1/public/ihbarlar",
            json={
                "aciklama": "Il disindan hatali ihbar denemesi.",
                "enlem": "41.0082000",
                "boylam": "28.9784000",
            },
        )

    assert response.status_code == 422
    assert "Gaziantep il sinirlari" in response.text


async def test_critical_container_update_creates_single_open_task(
    app,
    db_session: Session,
    operations_data,
) -> None:
    admin_token = await login_and_get_token(app, "admin@test.local", "Admin123!")
    konteyner = operations_data["konteyner"]

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        first = await client.post(
            f"/api/v1/operations/konteynerler/{konteyner.id}/doluluk",
            json={"doluluk_orani": 92},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        second = await client.post(
            f"/api/v1/operations/konteynerler/{konteyner.id}/doluluk",
            json={"doluluk_orani": 96},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["gorev_olusturuldu"] is True
    assert second.json()["gorev_olusturuldu"] is False

    gorevler = list(
        db_session.scalars(
            select(Gorev).where(
                Gorev.konteyner_id == konteyner.id,
                Gorev.tip == GorevTipi.KRITIK_KONTEYNER,
            )
        )
    )
    assert len(gorevler) == 1


async def test_container_fill_simulation_creates_task_for_critical_container(
    app,
    db_session: Session,
    operations_data,
) -> None:
    admin_token = await login_and_get_token(app, "admin@test.local", "Admin123!")
    konteyner = operations_data["konteyner"]
    konteyner.doluluk_orani = 84
    db_session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/v1/operations/konteynerler/doluluk-simulasyon",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["guncellenen_konteyner"] == 1
    assert payload["olusan_gorev_sayisi"] == 1
    assert payload["sonuclar"][0]["yeni_doluluk_orani"] >= 89
    assert payload["sonuclar"][0]["gorev_olusturuldu"] is True


async def test_driver_task_lifecycle_updates_related_records(
    app,
    db_session: Session,
    operations_data,
) -> None:
    admin_token = await login_and_get_token(app, "admin@test.local", "Admin123!")
    operator_token = await login_and_get_token(app, "operator@test.local", "Operator123!")
    driver_token = await login_and_get_token(app, "sofor@test.local", "Sofor123!")
    konteyner = operations_data["konteyner"]
    driver = operations_data["driver"]
    arac = operations_data["arac"]

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        create_response = await client.post(
            f"/api/v1/operations/konteynerler/{konteyner.id}/doluluk",
            json={"doluluk_orani": 90},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        gorev_id = create_response.json()["gorev_id"]

        assign_response = await client.post(
            f"/api/v1/operations/gorevler/{gorev_id}/ata",
            json={
                "sofor_id": driver.id,
                "arac_id": arac.id,
                "planlanan_tarih": datetime.now(timezone.utc).isoformat(),
                "sira_no": 1,
            },
            headers={"Authorization": f"Bearer {operator_token}"},
        )
        admin_list_response = await client.get(
            "/api/v1/operations/gorevler",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        list_response = await client.get(
            "/api/v1/operations/sofor/gorevler/gunluk",
            headers={"Authorization": f"Bearer {driver_token}"},
        )
        start_response = await client.post(
            f"/api/v1/operations/gorevler/{gorev_id}/baslat",
            headers={"Authorization": f"Bearer {driver_token}"},
        )
        complete_response = await client.post(
            f"/api/v1/operations/gorevler/{gorev_id}/sonuclandir",
            json={
                "sonuc": GorevSonucu.TAMAMLANDI.value,
                "aciklama": "Bosaltma tamamlandi.",
            },
            headers={"Authorization": f"Bearer {driver_token}"},
        )

    assert assign_response.status_code == 200
    assert admin_list_response.status_code == 200
    assert admin_list_response.json()["toplam"] == 1
    assert admin_list_response.json()["gorevler"][0]["durum"] == GorevDurumu.ATANDI.value
    assert list_response.status_code == 200
    assert list_response.json()["toplam"] == 1
    assert list_response.json()["gorevler"][0]["kullanilan_arac"]["plaka"] == arac.plaka
    assert start_response.json()["durum"] == GorevDurumu.ISLEMDE.value
    assert complete_response.json()["durum"] == GorevDurumu.TAMAMLANDI.value

    gorev = db_session.get(Gorev, gorev_id)
    konteyner_db = db_session.get(Konteyner, konteyner.id)
    assert gorev is not None
    assert gorev.durum == GorevDurumu.TAMAMLANDI
    assert konteyner_db is not None
    assert konteyner_db.durum == KonteynerDurumu.BOSALTILDI
    assert konteyner_db.doluluk_orani == 0

    log_count = len(
        list(
            db_session.scalars(
                select(IslemLog).where(
                    IslemLog.varlik_tipi == "Gorev",
                    IslemLog.varlik_id == gorev_id,
                )
            )
        )
    )
    assert log_count >= 3


async def test_driver_cannot_start_unassigned_task(app, operations_data) -> None:
    admin_token = await login_and_get_token(app, "admin@test.local", "Admin123!")
    driver_token = await login_and_get_token(app, "sofor@test.local", "Sofor123!")
    konteyner = operations_data["konteyner"]

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        create_response = await client.post(
            f"/api/v1/operations/konteynerler/{konteyner.id}/doluluk",
            json={"doluluk_orani": 88},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        gorev_id = create_response.json()["gorev_id"]
        start_response = await client.post(
            f"/api/v1/operations/gorevler/{gorev_id}/baslat",
            headers={"Authorization": f"Bearer {driver_token}"},
        )

    assert start_response.status_code == 403
