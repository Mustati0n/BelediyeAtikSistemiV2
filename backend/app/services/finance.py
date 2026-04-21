from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.entities import GelirKaydi, GiderKaydi, MaasOdeme, Personel
from backend.app.models.enums import OdemeDurumu, OdemeTipi, OnayDurumu
from backend.app.schemas.finance import BatchSalaryCreate, SalaryPaymentCreate

CHILD_ALLOWANCE = Decimal("1000.00")


def calculate_salary(personel: Personel) -> Decimal:
    return personel.taban_maas + (Decimal(personel.cocuk_sayisi) * CHILD_ALLOWANCE)


def get_personel_or_404(db: Session, personel_id: int) -> Personel:
    personel = db.get(Personel, personel_id)
    if personel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personel bulunamadi.")
    return personel


def create_salary_payment(db: Session, payload: SalaryPaymentCreate) -> MaasOdeme:
    personel = get_personel_or_404(db, payload.personel_id)
    _ensure_salary_period_available(
        db,
        personel_id=personel.id,
        donem_ay=payload.donem_ay,
        donem_yil=payload.donem_yil,
        odeme_tipi=payload.odeme_tipi,
    )

    payment = MaasOdeme(
        personel=personel,
        donem_ay=payload.donem_ay,
        donem_yil=payload.donem_yil,
        odeme_tarihi=payload.odeme_tarihi,
        tutar=payload.tutar,
        odeme_tipi=payload.odeme_tipi,
        durum=OdemeDurumu.ODENDI,
    )
    db.add(payment)
    db.flush()
    db.refresh(payment)
    return payment


def create_batch_salary_payments(db: Session, payload: BatchSalaryCreate) -> list[MaasOdeme]:
    if payload.odeme_tarihi.day != 15:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Toplu maas odemesi yalnizca ayin 15'inde yapilabilir.",
        )

    stmt = select(Personel).where(Personel.aktif_mi.is_(True)).order_by(Personel.id.asc())
    personeller = list(db.scalars(stmt))
    odemeler: list[MaasOdeme] = []

    for personel in personeller:
        _ensure_salary_period_available(
            db,
            personel_id=personel.id,
            donem_ay=payload.donem_ay,
            donem_yil=payload.donem_yil,
            odeme_tipi=OdemeTipi.TOPLU,
        )
        odeme = MaasOdeme(
            personel=personel,
            donem_ay=payload.donem_ay,
            donem_yil=payload.donem_yil,
            odeme_tarihi=payload.odeme_tarihi,
            tutar=calculate_salary(personel),
            odeme_tipi=OdemeTipi.TOPLU,
            durum=OdemeDurumu.ODENDI,
        )
        db.add(odeme)
        odemeler.append(odeme)

    db.flush()
    return odemeler


def profit_loss_summary(db: Session) -> dict[str, Decimal | int]:
    gelir_toplam = db.scalar(
        select(func.coalesce(func.sum(GelirKaydi.tutar), 0)).where(
            GelirKaydi.durum == OnayDurumu.ONAYLANDI
        )
    )
    gider_toplam = db.scalar(
        select(func.coalesce(func.sum(GiderKaydi.tutar), 0)).where(
            GiderKaydi.durum == OnayDurumu.ONAYLANDI
        )
    )
    bekleyen_gider = db.scalar(
        select(func.count()).select_from(GiderKaydi).where(GiderKaydi.durum == OnayDurumu.BEKLEMEDE)
    )
    bekleyen_gelir = db.scalar(
        select(func.count()).select_from(GelirKaydi).where(GelirKaydi.durum == OnayDurumu.BEKLEMEDE)
    )

    gelir_decimal = Decimal(str(gelir_toplam))
    gider_decimal = Decimal(str(gider_toplam))
    return {
        "onayli_gelir_toplami": gelir_decimal,
        "onayli_gider_toplami": gider_decimal,
        "net_sonuc": gelir_decimal - gider_decimal,
        "bekleyen_gider_sayisi": int(bekleyen_gider or 0),
        "bekleyen_gelir_sayisi": int(bekleyen_gelir or 0),
    }


def _ensure_salary_period_available(
    db: Session,
    *,
    personel_id: int,
    donem_ay: int,
    donem_yil: int,
    odeme_tipi: OdemeTipi,
) -> None:
    existing = db.scalar(
        select(MaasOdeme).where(
            MaasOdeme.personel_id == personel_id,
            MaasOdeme.donem_ay == donem_ay,
            MaasOdeme.donem_yil == donem_yil,
            MaasOdeme.odeme_tipi == odeme_tipi,
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ayni personel ve donem icin bu odeme tipi zaten mevcut.",
        )
