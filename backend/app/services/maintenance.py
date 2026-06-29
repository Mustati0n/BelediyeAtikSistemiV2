from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from backend.app.models.entities import Arac, BakimKaydi, GiderKaydi, Personel
from backend.app.models.enums import AracDurumu, BakimDurumu, OnayDurumu
from backend.app.schemas.maintenance import MaintenanceCreate


def create_maintenance_record(
    db: Session,
    payload: MaintenanceCreate,
    actor: Personel,
) -> BakimKaydi:
    arac = db.get(Arac, payload.arac_id)
    if arac is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arac bulunamadi.")
    if arac.durum == AracDurumu.BAKIMDA:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Arac zaten bakimda.",
        )

    detailed_cost = (payload.parca_maliyeti_tl or Decimal("0.00")) + (
        payload.iscilik_maliyeti_tl or Decimal("0.00")
    )
    total_cost = detailed_cost if detailed_cost > 0 else payload.maliyet_tl

    bakim = BakimKaydi(
        tarih=payload.tarih or datetime.now(timezone.utc),
        aciklama=payload.aciklama,
        bakim_turu=payload.bakim_turu,
        oncelik=payload.oncelik,
        maliyet_tl=total_cost,
        parca_maliyeti_tl=payload.parca_maliyeti_tl,
        iscilik_maliyeti_tl=payload.iscilik_maliyeti_tl,
        tedarikci=payload.tedarikci,
        kilometre=payload.kilometre,
        planlanan_tarih=payload.planlanan_tarih,
        durum=BakimDurumu.ACILDI,
        arac=arac,
        olusturan_personel=actor,
    )
    db.add(bakim)
    db.flush()

    gider = GiderKaydi(
        tarih=bakim.tarih,
        tutar=total_cost,
        aciklama=f"{arac.plaka} plakali arac bakim gideri",
        durum=OnayDurumu.BEKLEMEDE,
        bakim_kaydi=bakim,
    )
    db.add(gider)
    arac.durum = AracDurumu.BAKIMDA
    db.flush()
    db.refresh(bakim)
    return bakim


def complete_maintenance_technical(
    db: Session,
    bakim: BakimKaydi,
) -> BakimKaydi:
    if bakim.durum == BakimDurumu.IPTAL:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Iptal edilmis bakim teknik olarak tamamlanamaz.",
        )

    bakim.durum = BakimDurumu.TAMAMLANDI
    bakim.teknik_tamamlanma_tarihi = datetime.now(timezone.utc)
    bakim.arac.durum = AracDurumu.AKTIF
    db.flush()
    db.refresh(bakim)
    return bakim


def get_maintenance_or_404(db: Session, bakim_id: int) -> BakimKaydi:
    stmt = (
        select(BakimKaydi)
        .options(joinedload(BakimKaydi.arac), joinedload(BakimKaydi.gider_kaydi))
        .where(BakimKaydi.id == bakim_id)
    )
    bakim = db.scalar(stmt)
    if bakim is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bakim kaydi bulunamadi.",
        )
    return bakim


def list_maintenance_records(db: Session) -> list[BakimKaydi]:
    stmt = (
        select(BakimKaydi)
        .options(joinedload(BakimKaydi.arac), joinedload(BakimKaydi.gider_kaydi))
        .order_by(BakimKaydi.tarih.desc(), BakimKaydi.id.desc())
    )
    return list(db.scalars(stmt))


def list_pending_expenses(db: Session) -> list[GiderKaydi]:
    stmt = (
        select(GiderKaydi)
        .options(joinedload(GiderKaydi.bakim_kaydi).joinedload(BakimKaydi.arac))
        .where(GiderKaydi.durum == OnayDurumu.BEKLEMEDE)
        .order_by(GiderKaydi.tarih.asc(), GiderKaydi.id.asc())
    )
    return list(db.scalars(stmt))


def get_expense_or_404(db: Session, gider_id: int) -> GiderKaydi:
    stmt = (
        select(GiderKaydi)
        .options(joinedload(GiderKaydi.bakim_kaydi).joinedload(BakimKaydi.arac))
        .where(GiderKaydi.id == gider_id)
    )
    gider = db.scalar(stmt)
    if gider is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gider kaydi bulunamadi.",
        )
    return gider


def approve_expense(db: Session, gider: GiderKaydi) -> GiderKaydi:
    if gider.durum != OnayDurumu.BEKLEMEDE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sadece bekleyen giderler onaylanabilir.",
        )
    gider.durum = OnayDurumu.ONAYLANDI
    db.flush()
    db.refresh(gider)
    return gider


def reject_expense(db: Session, gider: GiderKaydi) -> GiderKaydi:
    if gider.durum != OnayDurumu.BEKLEMEDE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sadece bekleyen giderler reddedilebilir.",
        )
    gider.durum = OnayDurumu.REDDEDILDI
    db.flush()
    db.refresh(gider)
    return gider
