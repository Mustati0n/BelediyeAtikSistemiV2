from datetime import datetime
from decimal import Decimal

from backend.app.models.enums import AracDurumu, BakimDurumu, OnayDurumu
from backend.app.schemas.common import APIModel


class MaintenanceCreate(APIModel):
    arac_id: int
    aciklama: str
    maliyet_tl: Decimal
    tarih: datetime | None = None


class MaintenanceResponse(APIModel):
    id: int
    arac_id: int
    arac_plaka: str
    tarih: datetime
    aciklama: str
    maliyet_tl: Decimal
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
