from datetime import UTC, datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from backend.app.models.entities import GelirKaydi, Personel, Satis, Stok, StokHareketi, TesisTeslim
from backend.app.models.enums import AtikTipi, OnayDurumu
from backend.app.schemas.recycling import DeliveryCreate, SaleCreate, SortingCreate


def create_delivery(db: Session, payload: DeliveryCreate, driver: Personel) -> TesisTeslim:
    teslim = TesisTeslim(
        tarih=datetime.now(UTC),
        toplam_kg=payload.toplam_kg,
        aciklama=payload.aciklama,
        onaylandi_mi=False,
        teslim_eden_sofor=driver,
    )
    db.add(teslim)
    db.flush()
    db.refresh(teslim)
    return teslim


def get_delivery_or_404(db: Session, teslim_id: int) -> TesisTeslim:
    stmt = (
        select(TesisTeslim)
        .options(
            joinedload(TesisTeslim.teslim_eden_sofor),
            joinedload(TesisTeslim.teslim_alan_operator),
            joinedload(TesisTeslim.stok_hareketleri),
        )
        .where(TesisTeslim.id == teslim_id)
    )
    teslim = db.scalar(stmt)
    if teslim is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tesis teslim kaydi bulunamadi.",
        )
    return teslim


def approve_delivery(db: Session, teslim: TesisTeslim, operator: Personel) -> TesisTeslim:
    if teslim.onaylandi_mi:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu teslim kaydi zaten onaylanmis.",
        )
    teslim.onaylandi_mi = True
    teslim.onay_tarihi = datetime.now(UTC)
    teslim.teslim_alan_operator = operator
    db.flush()
    db.refresh(teslim)
    return teslim


def apply_sorting(db: Session, teslim: TesisTeslim, payload: SortingCreate) -> list[StokHareketi]:
    if not teslim.onaylandi_mi:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Onaylanmayan teslim kaydi icin ayristirma yapilamaz.",
        )
    if teslim.stok_hareketleri:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu teslim kaydi icin ayristirma zaten yapilmis.",
        )

    toplam = sum((hareket.miktar_kg for hareket in payload.hareketler), start=Decimal("0.000"))
    if toplam > teslim.toplam_kg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ayristirilan toplam miktar teslim edilen miktari asamaz.",
        )

    created: list[StokHareketi] = []
    for hareket in payload.hareketler:
        stok = _get_or_create_stock(db, hareket.atik_tipi)
        stok.toplam_miktar_kg += hareket.miktar_kg
        movement = StokHareketi(
            tarih=datetime.now(UTC),
            atik_tipi=hareket.atik_tipi,
            miktar_kg=hareket.miktar_kg,
            aciklama=hareket.aciklama,
            tesis_teslim=teslim,
            stok=stok,
        )
        db.add(movement)
        created.append(movement)

    db.flush()
    for movement in created:
        db.refresh(movement)
    return created


def list_stocks(db: Session) -> list[Stok]:
    stmt = select(Stok).order_by(Stok.atik_tipi.asc())
    return list(db.scalars(stmt))


def create_sale(db: Session, payload: SaleCreate) -> Satis:
    stok = db.scalar(select(Stok).where(Stok.atik_tipi == payload.atik_tipi))
    if stok is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Istenen atik tipi icin stok bulunamadi.",
        )
    if stok.toplam_miktar_kg < payload.miktar_kg:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Yeterli stok bulunmuyor.",
        )

    toplam_tutar = payload.miktar_kg * payload.birim_fiyat
    satis = Satis(
        tarih=datetime.now(UTC),
        miktar_kg=payload.miktar_kg,
        birim_fiyat=payload.birim_fiyat,
        toplam_tutar=toplam_tutar,
        durum=OnayDurumu.BEKLEMEDE,
        stok=stok,
    )
    db.add(satis)
    stok.toplam_miktar_kg -= payload.miktar_kg
    db.flush()

    gelir = GelirKaydi(
        tarih=satis.tarih,
        tutar=toplam_tutar,
        aciklama=f"{payload.atik_tipi.value} satis geliri",
        durum=OnayDurumu.BEKLEMEDE,
        satis=satis,
    )
    db.add(gelir)
    db.flush()
    db.refresh(satis)
    return satis


def list_pending_revenues(db: Session) -> list[GelirKaydi]:
    stmt = (
        select(GelirKaydi)
        .options(joinedload(GelirKaydi.satis).joinedload(Satis.stok))
        .where(GelirKaydi.durum == OnayDurumu.BEKLEMEDE)
        .order_by(GelirKaydi.tarih.asc(), GelirKaydi.id.asc())
    )
    return list(db.scalars(stmt))


def get_revenue_or_404(db: Session, gelir_id: int) -> GelirKaydi:
    stmt = (
        select(GelirKaydi)
        .options(joinedload(GelirKaydi.satis).joinedload(Satis.stok))
        .where(GelirKaydi.id == gelir_id)
    )
    gelir = db.scalar(stmt)
    if gelir is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gelir kaydi bulunamadi.")
    return gelir


def approve_revenue(db: Session, gelir: GelirKaydi) -> GelirKaydi:
    if gelir.durum != OnayDurumu.BEKLEMEDE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sadece bekleyen gelirler onaylanabilir.",
        )
    gelir.durum = OnayDurumu.ONAYLANDI
    if gelir.satis is not None:
        gelir.satis.durum = OnayDurumu.ONAYLANDI
    db.flush()
    db.refresh(gelir)
    return gelir


def reject_revenue(db: Session, gelir: GelirKaydi) -> GelirKaydi:
    if gelir.durum != OnayDurumu.BEKLEMEDE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sadece bekleyen gelirler reddedilebilir.",
        )
    gelir.durum = OnayDurumu.REDDEDILDI
    if gelir.satis is not None:
        gelir.satis.durum = OnayDurumu.REDDEDILDI
    db.flush()
    db.refresh(gelir)
    return gelir


def _get_or_create_stock(db: Session, atik_tipi: AtikTipi) -> Stok:
    stok = db.scalar(select(Stok).where(Stok.atik_tipi == atik_tipi))
    if stok is None:
        stok = Stok(atik_tipi=atik_tipi, toplam_miktar_kg=Decimal("0.000"))
        db.add(stok)
        db.flush()
    return stok
