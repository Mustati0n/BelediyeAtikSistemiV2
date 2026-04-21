from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.entities import Arac, Gorev, Ihbar, Konteyner, Personel
from backend.app.models.enums import (
    AracDurumu,
    GorevDurumu,
    GorevSonucu,
    GorevTipi,
    IhbarDurumu,
    KonteynerDurumu,
)
from backend.app.schemas.operations import (
    CitizenReportCreate,
    ContainerFillUpdateRequest,
    DriverTaskListResponse,
    DriverTaskSummary,
    TaskSourceSummary,
)

CRITICAL_FILL_THRESHOLD = 85
OPEN_TASK_STATUSES = (GorevDurumu.BEKLIYOR, GorevDurumu.ATANDI, GorevDurumu.ISLEMDE)


def create_citizen_report(db: Session, payload: CitizenReportCreate) -> tuple[Ihbar, Gorev]:
    now = datetime.now(UTC)
    ihbar = Ihbar(
        aciklama=payload.aciklama,
        enlem=payload.enlem,
        boylam=payload.boylam,
        fotograf_url=payload.fotograf_url,
        durum=IhbarDurumu.GOREVE_ATANDI,
        olusturma_tarihi=now,
    )
    db.add(ihbar)
    db.flush()

    gorev = Gorev(
        tip=GorevTipi.IHBAR,
        oncelik=10,
        durum=GorevDurumu.BEKLIYOR,
        planlanan_tarih=now,
        aciklama=payload.aciklama,
        ihbar_id=ihbar.id,
    )
    db.add(gorev)
    db.flush()
    db.refresh(ihbar)
    db.refresh(gorev)
    return ihbar, gorev


def update_container_fill(
    db: Session,
    konteyner: Konteyner,
    payload: ContainerFillUpdateRequest,
) -> tuple[Konteyner, Gorev | None]:
    konteyner.doluluk_orani = payload.doluluk_orani

    if payload.doluluk_orani >= CRITICAL_FILL_THRESHOLD:
        existing_task = db.scalar(_open_task_for_container_stmt(konteyner.id))
        if existing_task is not None:
            konteyner.durum = KonteynerDurumu.GOREVE_ATANDI
            db.flush()
            return konteyner, None

        konteyner.durum = KonteynerDurumu.KRITIK
        db.flush()

        gorev = Gorev(
            tip=GorevTipi.KRITIK_KONTEYNER,
            oncelik=8,
            durum=GorevDurumu.BEKLIYOR,
            planlanan_tarih=datetime.now(UTC),
            aciklama=f"{konteyner.kod} kodlu konteyner kritik doluluk seviyesine ulasti.",
            konteyner_id=konteyner.id,
        )
        db.add(gorev)
        db.flush()
        return konteyner, gorev

    konteyner.durum = (
        KonteynerDurumu.IZLENIYOR if payload.doluluk_orani >= 60 else KonteynerDurumu.NORMAL
    )
    db.flush()
    return konteyner, None


def assign_task(
    db: Session,
    gorev: Gorev,
    sofor: Personel,
    arac: Arac | None,
    *,
    planlanan_tarih: datetime | None,
    sira_no: int | None,
) -> Gorev:
    if gorev.durum not in {GorevDurumu.BEKLIYOR, GorevDurumu.ATANDI}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sadece bekleyen veya atanmis gorevler tekrar planlanabilir.",
        )
    if sofor.rol.ad != "Sofor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Atanan personel sofor rolunde olmali.",
        )
    if arac is not None and arac.durum != AracDurumu.AKTIF:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Goreve yalnizca aktif arac atanabilir.",
        )

    gorev.atanan_sofor_id = sofor.id
    gorev.kullanilan_arac_id = arac.id if arac is not None else None
    gorev.planlanan_tarih = planlanan_tarih or gorev.planlanan_tarih or datetime.now(UTC)
    gorev.sira_no = sira_no
    gorev.durum = GorevDurumu.ATANDI

    if gorev.ihbar is not None:
        gorev.ihbar.durum = IhbarDurumu.GOREVE_ATANDI
    if gorev.konteyner is not None:
        gorev.konteyner.durum = KonteynerDurumu.GOREVE_ATANDI

    db.flush()
    db.refresh(gorev)
    return gorev


def list_driver_tasks(db: Session, sofor_id: int) -> DriverTaskListResponse:
    stmt = (
        _task_with_source_stmt()
        .where(
            Gorev.atanan_sofor_id == sofor_id,
            Gorev.durum.in_([GorevDurumu.ATANDI, GorevDurumu.ISLEMDE]),
        )
        .order_by(
            Gorev.sira_no.is_(None),
            Gorev.sira_no.asc(),
            Gorev.oncelik.desc(),
            Gorev.id.asc(),
        )
    )
    gorevler = list(db.scalars(stmt))
    return DriverTaskListResponse(
        toplam=len(gorevler),
        gorevler=[_build_driver_task_summary(gorev) for gorev in gorevler],
    )


def start_task(db: Session, gorev: Gorev, sofor_id: int) -> Gorev:
    _ensure_driver_owns_task(gorev, sofor_id)
    if gorev.durum != GorevDurumu.ATANDI:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Gorev baslatilabilmesi icin once atanmis olmali.",
        )

    gorev.durum = GorevDurumu.ISLEMDE
    if gorev.ihbar is not None:
        gorev.ihbar.durum = IhbarDurumu.ISLEMDE
    db.flush()
    db.refresh(gorev)
    return gorev


def complete_task(
    db: Session,
    gorev: Gorev,
    sofor_id: int,
    *,
    sonuc: GorevSonucu,
    aciklama: str | None,
) -> Gorev:
    _ensure_driver_owns_task(gorev, sofor_id)
    if gorev.durum != GorevDurumu.ISLEMDE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Gorev sonuclandirilabilmesi icin islemde olmali.",
        )

    gorev.sonuc = sonuc
    gorev.aciklama = aciklama or gorev.aciklama
    gorev.tamamlanma_tarihi = datetime.now(UTC)
    gorev.durum = (
        GorevDurumu.TAMAMLANDI if sonuc == GorevSonucu.TAMAMLANDI else GorevDurumu.BASARISIZ
    )

    if gorev.ihbar is not None:
        _apply_ihbar_result(gorev.ihbar, sonuc)
    if gorev.konteyner is not None:
        _apply_container_result(gorev.konteyner, sonuc)

    db.flush()
    db.refresh(gorev)
    return gorev


def get_task_with_source(db: Session, gorev_id: int) -> Gorev:
    stmt = _task_with_source_stmt().where(Gorev.id == gorev_id)
    gorev = db.scalar(stmt)
    if gorev is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gorev bulunamadi.")
    return gorev


def get_container_or_404(db: Session, konteyner_id: int) -> Konteyner:
    konteyner = db.get(Konteyner, konteyner_id)
    if konteyner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Konteyner bulunamadi.")
    return konteyner


def get_personel_or_404(db: Session, personel_id: int) -> Personel:
    stmt = select(Personel).options(selectinload(Personel.rol)).where(Personel.id == personel_id)
    personel = db.scalar(stmt)
    if personel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personel bulunamadi.")
    return personel


def get_arac_or_404(db: Session, arac_id: int) -> Arac:
    arac = db.get(Arac, arac_id)
    if arac is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arac bulunamadi.")
    return arac


def _apply_ihbar_result(ihbar: Ihbar, sonuc: GorevSonucu) -> None:
    if sonuc == GorevSonucu.TAMAMLANDI:
        ihbar.durum = IhbarDurumu.COZULDU
    elif sonuc == GorevSonucu.YANLIS_IHBAR:
        ihbar.durum = IhbarDurumu.GECERSIZ
    else:
        ihbar.durum = IhbarDurumu.BEKLIYOR


def _apply_container_result(konteyner: Konteyner, sonuc: GorevSonucu) -> None:
    if sonuc == GorevSonucu.TAMAMLANDI:
        konteyner.durum = KonteynerDurumu.BOSALTILDI
        konteyner.doluluk_orani = 0
    elif sonuc == GorevSonucu.TEKRAR_KONTROL_GEREKLI:
        konteyner.durum = KonteynerDurumu.KRITIK
    else:
        konteyner.durum = KonteynerDurumu.IZLENIYOR


def _ensure_driver_owns_task(gorev: Gorev, sofor_id: int) -> None:
    if gorev.atanan_sofor_id != sofor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu gorev size atanmamis.",
        )


def _open_task_for_container_stmt(konteyner_id: int) -> Select[tuple[Gorev]]:
    return select(Gorev).where(
        Gorev.konteyner_id == konteyner_id,
        Gorev.durum.in_(OPEN_TASK_STATUSES),
    )


def _task_with_source_stmt() -> Select[tuple[Gorev]]:
    return select(Gorev).options(
        selectinload(Gorev.ihbar),
        selectinload(Gorev.konteyner),
        selectinload(Gorev.atanan_sofor).selectinload(Personel.rol),
        selectinload(Gorev.kullanilan_arac),
    )


def _build_driver_task_summary(gorev: Gorev) -> DriverTaskSummary:
    if gorev.ihbar is not None:
        kaynak = TaskSourceSummary(
            tip="Ihbar",
            id=gorev.ihbar.id,
            aciklama=gorev.ihbar.aciklama,
            enlem=gorev.ihbar.enlem,
            boylam=gorev.ihbar.boylam,
            durum=gorev.ihbar.durum.value,
        )
    elif gorev.konteyner is not None:
        kaynak = TaskSourceSummary(
            tip="Konteyner",
            id=gorev.konteyner.id,
            aciklama=f"{gorev.konteyner.kod} kodlu konteyner",
            enlem=gorev.konteyner.enlem,
            boylam=gorev.konteyner.boylam,
            durum=gorev.konteyner.durum.value,
        )
    else:
        raise ValueError("Gorev kaynaksiz olamaz.")

    return DriverTaskSummary(
        id=gorev.id,
        tip=gorev.tip,
        durum=gorev.durum,
        oncelik=gorev.oncelik,
        planlanan_tarih=gorev.planlanan_tarih,
        sira_no=gorev.sira_no,
        aciklama=gorev.aciklama,
        kullanilan_arac_id=gorev.kullanilan_arac_id,
        kaynak=kaynak,
    )
