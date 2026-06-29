from datetime import datetime
from decimal import Decimal

from backend.app.models.enums import AracDurumu, BakimDurumu, OnayDurumu
from backend.app.schemas.common import APIModel


class MaintenanceCreate(APIModel):
    arac_id: int
    aciklama: str
    maliyet_tl: Decimal
    tarih: datetime | None = None
    bakim_turu: str | None = None
    oncelik: str | None = None
    parca_maliyeti_tl: Decimal | None = None
    iscilik_maliyeti_tl: Decimal | None = None
    tedarikci: str | None = None
    kilometre: int | None = None
    planlanan_tarih: datetime | None = None


class MaintenanceResponse(APIModel):
    id: int
    arac_id: int
    arac_plaka: str
    tarih: datetime
    aciklama: str
    bakim_turu: str | None
    oncelik: str | None
    maliyet_tl: Decimal
    parca_maliyeti_tl: Decimal | None
    iscilik_maliyeti_tl: Decimal | None
    tedarikci: str | None
    kilometre: int | None
    planlanan_tarih: datetime | None
    durum: BakimDurumu
    teknik_tamamlanma_tarihi: datetime | None
    arac_durumu: AracDurumu
    gider_kaydi_id: int | None
    gider_durumu: OnayDurumu | None


class PendingExpenseResponse(APIModel):
    id: int
    tarih: datetime
    tutar: Decimal
    aciklama: str
    durum: OnayDurumu
    bakim_kaydi_id: int | None
    arac_plaka: str | None


class ExpenseDecisionResponse(APIModel):
    gider_id: int
    durum: OnayDurumu
    mesaj: str
