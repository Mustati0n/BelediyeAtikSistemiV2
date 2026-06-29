from decimal import Decimal

from backend.app.schemas.common import APIModel


class CountByStatus(APIModel):
    durum: str
    sayi: int


class FinanceSnapshot(APIModel):
    onayli_gelir_toplami: Decimal
    onayli_gider_toplami: Decimal
    net_sonuc: Decimal
    bekleyen_gider_sayisi: int
    bekleyen_gelir_sayisi: int


class AdminModuleSnapshot(APIModel):
    toplam: int
    durumlar: list[CountByStatus]


class AdminTaskSnapshot(AdminModuleSnapshot):
    bekleyen: int
    atanmis: int
    islemde: int


class RecentAuditLog(APIModel):
    id: int
    islem_tipi: str
    aciklama: str
    varlik_tipi: str
    varlik_id: int | None
    islem_tarihi: str
    yapan: str | None = None


class AdminLogListResponse(APIModel):
    toplam: int
    loglar: list[RecentAuditLog]


class AdminDashboardSummary(APIModel):
    araclar: AdminModuleSnapshot
    personel: AdminModuleSnapshot
    konteynerler: AdminModuleSnapshot
    gorevler: AdminTaskSnapshot
    bakim: AdminModuleSnapshot
    tesis_teslimleri: AdminModuleSnapshot
    stok_toplam_kg: Decimal
    finans: FinanceSnapshot
    son_islemler: list[RecentAuditLog]
