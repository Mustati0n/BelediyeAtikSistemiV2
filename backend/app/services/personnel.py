from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from backend.app.core.security import get_password_hash
from backend.app.models.entities import Personel, Rol
from backend.app.schemas.personnel import PersonnelCreate, PersonnelUpdate


def list_roles(db: Session) -> list[Rol]:
    return list(db.scalars(select(Rol).order_by(Rol.ad.asc())))


def get_role_or_404(db: Session, role_id: int) -> Rol:
    role = db.get(Rol, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol bulunamadi.")
    return role


def list_personnel(db: Session) -> list[Personel]:
    stmt = select(Personel).options(joinedload(Personel.rol)).order_by(Personel.ad_soyad.asc())
    return list(db.scalars(stmt))


def get_personnel_or_404(db: Session, personel_id: int) -> Personel:
    stmt = (
        select(Personel)
        .options(joinedload(Personel.rol))
        .where(Personel.id == personel_id)
    )
    personel = db.scalar(stmt)
    if personel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personel bulunamadi.")
    return personel


def create_personnel(db: Session, payload: PersonnelCreate) -> Personel:
    role = get_role_or_404(db, payload.rol_id)
    personel = Personel(
        tc_no=payload.tc_no,
        sifre_hash=get_password_hash(payload.password),
        ad_soyad=payload.ad_soyad,
        email=str(payload.email),
        telefon=payload.telefon,
        taban_maas=payload.taban_maas,
        cocuk_sayisi=payload.cocuk_sayisi,
        aktif_mi=True,
        rol=role,
    )
    db.add(personel)
    _flush_or_conflict(db)
    db.refresh(personel)
    return personel


def update_personnel(db: Session, personel: Personel, payload: PersonnelUpdate) -> Personel:
    updates = payload.model_dump(exclude_unset=True)
    if "rol_id" in updates and updates["rol_id"] is not None:
        personel.rol = get_role_or_404(db, updates.pop("rol_id"))

    password = updates.pop("password", None)
    if password:
        personel.sifre_hash = get_password_hash(password)

    for field, value in updates.items():
        if field == "email" and value is not None:
            value = str(value)
        setattr(personel, field, value)

    _flush_or_conflict(db)
    db.refresh(personel)
    return personel


def _flush_or_conflict(db: Session) -> None:
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="TC no veya e-posta zaten kullaniliyor.",
        ) from exc
