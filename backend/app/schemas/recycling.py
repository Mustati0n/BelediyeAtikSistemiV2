from datetime import datetime
from decimal import Decimal

from backend.app.models.enums import AtikTipi, OnayDurumu
from backend.app.schemas.common import APIModel


class DeliveryCreate(APIModel):
    toplam_kg: Decimal
    aciklama: str | None = None


class DeliveryResponse(APIModel):
    id: int
    tarih: datetime
    toplam_kg: Decimal
    aciklama: str | None
    onaylandi_mi: bool
    onay_tarihi: datetime | None
    teslim_eden_sofor_id: int
    teslim_alan_operator_id: int | None


class DeliveryApprovalResponse(APIModel):
    teslim_id: int
    onaylandi_mi: bool
    mesaj: str


class SortingItem(APIModel):
    atik_tipi: AtikTipi
    miktar_kg: Decimal
    aciklama: str | None = None


class SortingCreate(APIModel):
    hareketler: list[SortingItem]


class StockMovementResponse(APIModel):
    id: int
    atik_tipi: AtikTipi
    miktar_kg: Decimal
    aciklama: str | None
    stok_id: int
    tesis_teslim_id: int


class SortingResponse(APIModel):
    teslim_id: int
    hareket_sayisi: int
    hareketler: list[StockMovementResponse]


class StockResponse(APIModel):
    id: int
    atik_tipi: AtikTipi
    toplam_miktar_kg: Decimal


class SaleCreate(APIModel):
    atik_tipi: AtikTipi
    miktar_kg: Decimal
    birim_fiyat: Decimal


class SaleResponse(APIModel):
    satis_id: int
    stok_id: int
    atik_tipi: AtikTipi
    miktar_kg: Decimal
    birim_fiyat: Decimal
    toplam_tutar: Decimal
    durum: OnayDurumu
    gelir_kaydi_id: int | None
    gelir_durumu: OnayDurumu | None


class PendingRevenueResponse(APIModel):
    id: int
    tarih: datetime
    tutar: Decimal
    aciklama: str
    durum: OnayDurumu
    satis_id: int | None


class RevenueDecisionResponse(APIModel):
    gelir_id: int
    durum: OnayDurumu
    mesaj: str
