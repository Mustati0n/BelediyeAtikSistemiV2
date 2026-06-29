from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from backend.app.models.entities import Bolge, Gorev, Konteyner
from backend.app.models.enums import GorevDurumu
from backend.app.schemas.containers import ContainerCreate, ContainerUpdate, RegionCreate


def list_regions(db: Session) -> list[Bolge]:
    return list(db.scalars(select(Bolge).order_by(Bolge.ad.asc())))


def get_region_or_404(db: Session, region_id: int) -> Bolge:
    region = db.get(Bolge, region_id)
    if region is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bolge bulunamadi.")
    return region


def create_region(db: Session, payload: RegionCreate) -> Bolge:
    region = Bolge(ad=payload.ad, aciklama=payload.aciklama)
    db.add(region)
    _flush_or_conflict(db, "Bolge adi zaten kullaniliyor.")
    db.refresh(region)
    return region


def list_containers(db: Session) -> list[Konteyner]:
    stmt = select(Konteyner).options(joinedload(Konteyner.bolge)).order_by(Konteyner.kod.asc())
    return list(db.scalars(stmt))


def get_container_or_404(db: Session, container_id: int) -> Konteyner:
    stmt = (
        select(Konteyner)
        .options(joinedload(Konteyner.bolge))
        .where(Konteyner.id == container_id)
    )
    container = db.scalar(stmt)
    if container is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Konteyner bulunamadi.")
    return container


def create_container(db: Session, payload: ContainerCreate) -> Konteyner:
    region = get_region_or_404(db, payload.bolge_id)
    container = Konteyner(
        kod=payload.kod,
        enlem=payload.enlem,
        boylam=payload.boylam,
        doluluk_orani=payload.doluluk_orani,
        durum=payload.durum,
        bolge=region,
    )
    db.add(container)
    _flush_or_conflict(db, "Konteyner kodu zaten kullaniliyor.")
    db.refresh(container)
    return container


def update_container(db: Session, container: Konteyner, payload: ContainerUpdate) -> Konteyner:
    updates = payload.model_dump(exclude_unset=True)
    if "bolge_id" in updates and updates["bolge_id"] is not None:
        container.bolge = get_region_or_404(db, updates.pop("bolge_id"))

    for field, value in updates.items():
        setattr(container, field, value)

    _flush_or_conflict(db, "Konteyner kodu zaten kullaniliyor.")
    db.refresh(container)
    return container


def delete_container(db: Session, container: Konteyner) -> None:
    open_task = db.scalar(
        select(Gorev)
        .where(
            Gorev.konteyner_id == container.id,
            Gorev.durum.in_(
                [
                    GorevDurumu.BEKLIYOR,
                    GorevDurumu.ATANDI,
                    GorevDurumu.ISLEMDE,
                ],
            ),
        )
        .limit(1)
    )
    if open_task is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu konteynere bagli acik gorev oldugu icin silinemez.",
        )

    db.delete(container)
    db.flush()


def _flush_or_conflict(db: Session, detail: str) -> None:
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from exc
