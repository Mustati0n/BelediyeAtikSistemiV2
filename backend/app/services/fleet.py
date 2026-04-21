from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.entities import Arac
from backend.app.schemas.fleet import VehicleCreate, VehicleUpdate


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
        arac.durum = payload.durum

    db.flush()
    db.refresh(arac)
    return arac
