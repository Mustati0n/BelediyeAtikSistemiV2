from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.entities import Arac, BakimKaydi, GelirKaydi
from backend.app.models.enums import AracDurumu, OnayDurumu
from backend.app.schemas.fleet import VehicleCreate, VehicleScrapSaleRequest, VehicleUpdate


def create_vehicle(db: Session, payload: VehicleCreate) -> Arac:
    existing = db.scalar(select(Arac).where(Arac.plaka == payload.plaka))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu plakaya sahip arac zaten mevcut.",
        )

    arac = Arac(
        plaka=payload.plaka.upper(),
        tip=payload.tip,
        kapasite_kg=payload.kapasite_kg,
    )
    db.add(arac)
    db.flush()
    db.refresh(arac)
    return arac


def list_vehicles(db: Session) -> list[Arac]:
    stmt = select(Arac).order_by(Arac.plaka.asc())
    return list(db.scalars(stmt))


def get_vehicle_or_404(db: Session, arac_id: int) -> Arac:
    arac = db.get(Arac, arac_id)
    if arac is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arac bulunamadi.")
    return arac


def update_vehicle(db: Session, arac: Arac, payload: VehicleUpdate) -> Arac:
    if payload.tip is not None:
        arac.tip = payload.tip
    if payload.kapasite_kg is not None:
        arac.kapasite_kg = payload.kapasite_kg
    if payload.durum is not None:
        if payload.durum == AracDurumu.HURDA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hurda islemi icin hurda satis aksiyonunu kullanin.",
            )
        arac.durum = payload.durum

    db.flush()
    db.refresh(arac)
    return arac


def scrap_and_sell_vehicle(db: Session, arac: Arac, payload: VehicleScrapSaleRequest) -> tuple[Arac, GelirKaydi]:
    _ensure_vehicle_scrappable(db, arac)
    arac.durum = AracDurumu.HURDA
    gelir = GelirKaydi(
        tarih=datetime.now(timezone.utc),
        tutar=payload.satis_tutari,
        aciklama=payload.aciklama or f"{arac.plaka} plakali arac hurda satis geliri",
        durum=OnayDurumu.BEKLEMEDE,
    )
    db.add(gelir)
    db.flush()
    db.refresh(arac)
    db.refresh(gelir)
    return arac, gelir


def _ensure_vehicle_scrappable(db: Session, arac: Arac) -> None:
    if arac.durum in {AracDurumu.BAKIMDA, AracDurumu.PASIF, AracDurumu.HURDA}:
        return
    stmt = (
        select(BakimKaydi)
        .where(BakimKaydi.arac_id == arac.id)
        .order_by(BakimKaydi.kilometre.desc().nullslast(), BakimKaydi.id.desc())
    )
    latest_maintenance = db.scalar(stmt)
    if latest_maintenance and latest_maintenance.kilometre and latest_maintenance.kilometre >= 200000:
        return
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Arac hurdaya ayrilamaz. Arac pasif/bakimda olmali veya son bakim km bilgisi 200.000 km ustunde olmalidir.",
    )
