from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.entities import GelirKaydi, IslemLog, Satis, Stok, TesisTeslim
from backend.app.models.enums import AtikTipi, OnayDurumu

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


async def test_delivery_approval_sorting_and_stock_listing(
    app,
    db_session: Session,
    seeded_users,
) -> None:
    driver_token = await login_and_get_token(app, "sofor@test.local", "Sofor123!")
    operator_token = await login_and_get_token(app, "operator@test.local", "Operator123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        create_response = await client.post(
            "/api/v1/recycling/teslimler",
            json={"toplam_kg": "120.000", "aciklama": "Gun sonu teslimi"},
            headers={"Authorization": f"Bearer {driver_token}"},
        )
        teslim_id = create_response.json()["id"]

        approve_response = await client.post(
            f"/api/v1/recycling/teslimler/{teslim_id}/onayla",
            headers={"Authorization": f"Bearer {operator_token}"},
        )
        sorting_response = await client.post(
            f"/api/v1/recycling/teslimler/{teslim_id}/ayristir",
            json={
                "hareketler": [
                    {"atik_tipi": AtikTipi.PLASTIK.value, "miktar_kg": "50.000"},
                    {"atik_tipi": AtikTipi.CAM.value, "miktar_kg": "30.000"},
                ]
            },
            headers={"Authorization": f"Bearer {operator_token}"},
        )
        stocks_response = await client.get(
            "/api/v1/recycling/stoklar",
            headers={"Authorization": f"Bearer {operator_token}"},
        )

    assert create_response.status_code == 201
    assert approve_response.status_code == 200
    assert sorting_response.status_code == 200
    assert sorting_response.json()["hareket_sayisi"] == 2
    assert stocks_response.status_code == 200
    assert len(stocks_response.json()) == 2

    teslim = db_session.get(TesisTeslim, teslim_id)
    assert teslim is not None
    assert teslim.onaylandi_mi is True


async def test_operator_cannot_sort_unapproved_delivery(app, seeded_users) -> None:
    driver_token = await login_and_get_token(app, "sofor@test.local", "Sofor123!")
    operator_token = await login_and_get_token(app, "operator@test.local", "Operator123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        create_response = await client.post(
            "/api/v1/recycling/teslimler",
            json={"toplam_kg": "40.000"},
            headers={"Authorization": f"Bearer {driver_token}"},
        )
        teslim_id = create_response.json()["id"]
        sorting_response = await client.post(
            f"/api/v1/recycling/teslimler/{teslim_id}/ayristir",
            json={"hareketler": [{"atik_tipi": AtikTipi.METAL.value, "miktar_kg": "10.000"}]},
            headers={"Authorization": f"Bearer {operator_token}"},
        )

    assert sorting_response.status_code == 409


async def test_sale_creates_pending_revenue_and_reduces_stock(
    app,
    db_session: Session,
    seeded_users,
) -> None:
    driver_token = await login_and_get_token(app, "sofor@test.local", "Sofor123!")
    operator_token = await login_and_get_token(app, "operator@test.local", "Operator123!")
    finance_token = await login_and_get_token(app, "muhasebe@test.local", "Muhasebe123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        teslim = await client.post(
            "/api/v1/recycling/teslimler",
            json={"toplam_kg": "100.000"},
            headers={"Authorization": f"Bearer {driver_token}"},
        )
        teslim_id = teslim.json()["id"]
        await client.post(
            f"/api/v1/recycling/teslimler/{teslim_id}/onayla",
            headers={"Authorization": f"Bearer {operator_token}"},
        )
        await client.post(
            f"/api/v1/recycling/teslimler/{teslim_id}/ayristir",
            json={"hareketler": [{"atik_tipi": AtikTipi.PLASTIK.value, "miktar_kg": "80.000"}]},
            headers={"Authorization": f"Bearer {operator_token}"},
        )
        sale_response = await client.post(
            "/api/v1/recycling/satislar",
            json={
                "atik_tipi": AtikTipi.PLASTIK.value,
                "miktar_kg": "30.000",
                "birim_fiyat": "12.50",
            },
            headers={"Authorization": f"Bearer {operator_token}"},
        )
        pending_response = await client.get(
            "/api/v1/recycling/gelirler/bekleyen",
            headers={"Authorization": f"Bearer {finance_token}"},
        )

    assert sale_response.status_code == 201
    payload = sale_response.json()
    assert payload["toplam_tutar"] == "375.00"
    assert payload["durum"] == OnayDurumu.BEKLEMEDE.value
    assert pending_response.status_code == 200
    assert len(pending_response.json()) == 1

    stok = db_session.scalar(select(Stok).where(Stok.atik_tipi == AtikTipi.PLASTIK))
    assert stok is not None
    assert stok.toplam_miktar_kg == Decimal("50.000")


async def test_revenue_approval_and_rejection_flow(
    app,
    db_session: Session,
    seeded_users,
) -> None:
    driver_token = await login_and_get_token(app, "sofor@test.local", "Sofor123!")
    operator_token = await login_and_get_token(app, "operator@test.local", "Operator123!")
    finance_token = await login_and_get_token(app, "muhasebe@test.local", "Muhasebe123!")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        teslim = await client.post(
            "/api/v1/recycling/teslimler",
            json={"toplam_kg": "70.000"},
            headers={"Authorization": f"Bearer {driver_token}"},
        )
        teslim_id = teslim.json()["id"]
        await client.post(
            f"/api/v1/recycling/teslimler/{teslim_id}/onayla",
            headers={"Authorization": f"Bearer {operator_token}"},
        )
        await client.post(
            f"/api/v1/recycling/teslimler/{teslim_id}/ayristir",
            json={"hareketler": [{"atik_tipi": AtikTipi.CAM.value, "miktar_kg": "60.000"}]},
            headers={"Authorization": f"Bearer {operator_token}"},
        )
        first_sale = await client.post(
            "/api/v1/recycling/satislar",
            json={
                "atik_tipi": AtikTipi.CAM.value,
                "miktar_kg": "10.000",
                "birim_fiyat": "8.00",
            },
            headers={"Authorization": f"Bearer {operator_token}"},
        )
        second_sale = await client.post(
            "/api/v1/recycling/satislar",
            json={
                "atik_tipi": AtikTipi.CAM.value,
                "miktar_kg": "5.000",
                "birim_fiyat": "9.00",
            },
            headers={"Authorization": f"Bearer {operator_token}"},
        )

        first_approve = await client.post(
            f"/api/v1/recycling/gelirler/{first_sale.json()['gelir_kaydi_id']}/onayla",
            headers={"Authorization": f"Bearer {finance_token}"},
        )
        second_reject = await client.post(
            f"/api/v1/recycling/gelirler/{second_sale.json()['gelir_kaydi_id']}/reddet",
            headers={"Authorization": f"Bearer {finance_token}"},
        )

    assert first_approve.status_code == 200
    assert second_reject.status_code == 200

    gelirler = list(db_session.scalars(select(GelirKaydi)))
    assert len(gelirler) == 2
    assert {gelir.durum for gelir in gelirler} == {OnayDurumu.ONAYLANDI, OnayDurumu.REDDEDILDI}

    satislar = list(db_session.scalars(select(Satis)))
    assert {satis.durum for satis in satislar} == {OnayDurumu.ONAYLANDI, OnayDurumu.REDDEDILDI}

    logs = list(db_session.scalars(select(IslemLog)))
    assert len(logs) >= 6
