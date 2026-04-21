from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.deps import require_roles
from backend.app.db.session import get_db
from backend.app.models.entities import Personel
from backend.app.schemas.recycling import (
    DeliveryApprovalResponse,
    DeliveryCreate,
    DeliveryResponse,
    PendingRevenueResponse,
    RevenueDecisionResponse,
    SaleCreate,
    SaleResponse,
    SortingCreate,
    SortingResponse,
    StockMovementResponse,
    StockResponse,
)
from backend.app.services.audit import log_action
from backend.app.services.recycling import (
    apply_sorting,
    approve_delivery,
    approve_revenue,
    create_delivery,
    create_sale,
    get_delivery_or_404,
    get_revenue_or_404,
    list_pending_revenues,
    list_stocks,
    reject_revenue,
)

router = APIRouter(prefix="/recycling", tags=["recycling"])

DBSession = Annotated[Session, Depends(get_db)]
DriverUser = Annotated[Personel, Depends(require_roles("Sofor"))]
OperatorUser = Annotated[
    Personel,
    Depends(require_roles("Geri Donusum Operatoru", "Sistem Yoneticisi")),
]
FinanceUser = Annotated[
    Personel,
    Depends(require_roles("Muhasebe Personeli", "Sistem Yoneticisi")),
]


@router.post("/teslimler", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
def create_delivery_endpoint(
    payload: DeliveryCreate,
    db: DBSession,
    current_user: DriverUser,
) -> DeliveryResponse:
    teslim = create_delivery(db, payload, current_user)
    log_action(
        db,
        actor=current_user,
        islem_tipi="TesisTeslimOlustur",
        aciklama=f"{teslim.id} numarali tesis teslim kaydi olusturuldu.",
        varlik_tipi="TesisTeslim",
        varlik_id=teslim.id,
    )
    db.commit()
    return DeliveryResponse.model_validate(teslim)


@router.post("/teslimler/{teslim_id}/onayla", response_model=DeliveryApprovalResponse)
def approve_delivery_endpoint(
    teslim_id: int,
    db: DBSession,
    current_user: OperatorUser,
) -> DeliveryApprovalResponse:
    teslim = get_delivery_or_404(db, teslim_id)
    teslim = approve_delivery(db, teslim, current_user)
    log_action(
        db,
        actor=current_user,
        islem_tipi="TesisTeslimOnayla",
        aciklama=f"{teslim.id} numarali teslim operator tarafindan onaylandi.",
        varlik_tipi="TesisTeslim",
        varlik_id=teslim.id,
    )
    db.commit()
    return DeliveryApprovalResponse(
        teslim_id=teslim.id,
        onaylandi_mi=teslim.onaylandi_mi,
        mesaj="Tesis teslim kaydi onaylandi.",
    )


@router.post("/teslimler/{teslim_id}/ayristir", response_model=SortingResponse)
def apply_sorting_endpoint(
    teslim_id: int,
    payload: SortingCreate,
    db: DBSession,
    current_user: OperatorUser,
) -> SortingResponse:
    teslim = get_delivery_or_404(db, teslim_id)
    hareketler = apply_sorting(db, teslim, payload)
    log_action(
        db,
        actor=current_user,
        islem_tipi="StokAyristirma",
        aciklama=f"{teslim.id} numarali teslim icin stok ayristirma yapildi.",
        varlik_tipi="TesisTeslim",
        varlik_id=teslim.id,
    )
    db.commit()
    return SortingResponse(
        teslim_id=teslim.id,
        hareket_sayisi=len(hareketler),
        hareketler=[StockMovementResponse.model_validate(hareket) for hareket in hareketler],
    )


@router.get("/stoklar", response_model=list[StockResponse])
def read_stocks(
    db: DBSession,
    _: OperatorUser,
) -> list[StockResponse]:
    stoklar = list_stocks(db)
    return [StockResponse.model_validate(stok) for stok in stoklar]


@router.post("/satislar", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale_endpoint(
    payload: SaleCreate,
    db: DBSession,
    current_user: OperatorUser,
) -> SaleResponse:
    satis = create_sale(db, payload)
    log_action(
        db,
        actor=current_user,
        islem_tipi="SatisOlustur",
        aciklama=f"{satis.id} numarali satis kaydi olusturuldu.",
        varlik_tipi="Satis",
        varlik_id=satis.id,
    )
    db.commit()
    return _build_sale_response(satis)


@router.get("/gelirler/bekleyen", response_model=list[PendingRevenueResponse])
def read_pending_revenues(
    db: DBSession,
    _: FinanceUser,
) -> list[PendingRevenueResponse]:
    gelirler = list_pending_revenues(db)
    return [
        PendingRevenueResponse(
            id=gelir.id,
            tarih=gelir.tarih,
            tutar=gelir.tutar,
            aciklama=gelir.aciklama,
            durum=gelir.durum,
            satis_id=gelir.satis_id,
        )
        for gelir in gelirler
    ]


@router.post("/gelirler/{gelir_id}/onayla", response_model=RevenueDecisionResponse)
def approve_revenue_endpoint(
    gelir_id: int,
    db: DBSession,
    current_user: FinanceUser,
) -> RevenueDecisionResponse:
    gelir = get_revenue_or_404(db, gelir_id)
    gelir = approve_revenue(db, gelir)
    log_action(
        db,
        actor=current_user,
        islem_tipi="GelirOnayla",
        aciklama=f"{gelir.id} numarali gelir onaylandi.",
        varlik_tipi="GelirKaydi",
        varlik_id=gelir.id,
    )
    db.commit()
    return RevenueDecisionResponse(
        gelir_id=gelir.id,
        durum=gelir.durum,
        mesaj="Gelir kaydi onaylandi.",
    )


@router.post("/gelirler/{gelir_id}/reddet", response_model=RevenueDecisionResponse)
def reject_revenue_endpoint(
    gelir_id: int,
    db: DBSession,
    current_user: FinanceUser,
) -> RevenueDecisionResponse:
    gelir = get_revenue_or_404(db, gelir_id)
    gelir = reject_revenue(db, gelir)
    log_action(
        db,
        actor=current_user,
        islem_tipi="GelirReddet",
        aciklama=f"{gelir.id} numarali gelir reddedildi.",
        varlik_tipi="GelirKaydi",
        varlik_id=gelir.id,
    )
    db.commit()
    return RevenueDecisionResponse(
        gelir_id=gelir.id,
        durum=gelir.durum,
        mesaj="Gelir kaydi reddedildi.",
    )


def _build_sale_response(satis) -> SaleResponse:
    return SaleResponse(
        satis_id=satis.id,
        stok_id=satis.stok_id,
        atik_tipi=satis.stok.atik_tipi,
        miktar_kg=satis.miktar_kg,
        birim_fiyat=satis.birim_fiyat,
        toplam_tutar=satis.toplam_tutar,
        durum=satis.durum,
        gelir_kaydi_id=satis.gelir_kaydi.id if satis.gelir_kaydi is not None else None,
        gelir_durumu=satis.gelir_kaydi.durum if satis.gelir_kaydi is not None else None,
    )
