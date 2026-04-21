from datetime import date
from decimal import Decimal

from backend.app.models.enums import OdemeDurumu, OdemeTipi
from backend.app.schemas.common import APIModel


class SalaryCalculationResponse(APIModel):
    personel_id: int
    ad_soyad: str
    taban_maas: Decimal
    cocuk_sayisi: int
    cocuk_destegi: Decimal
    toplam_hesaplanan_maas: Decimal


class SalaryPaymentCreate(APIModel):
    personel_id: int
    donem_ay: int
    donem_yil: int
    odeme_tarihi: date
    tutar: Decimal
    aciklama: str | None = None
    odeme_tipi: OdemeTipi


class BatchSalaryCreate(APIModel):
    donem_ay: int
    donem_yil: int
    odeme_tarihi: date


class SalaryPaymentResponse(APIModel):
    id: int
    personel_id: int
    ad_soyad: str
    tutar: Decimal
    odeme_tipi: OdemeTipi
    durum: OdemeDurumu
    donem_ay: int
    donem_yil: int
    odeme_tarihi: date


class BatchSalaryResponse(APIModel):
    toplam_odeme: Decimal
    kayit_sayisi: int
    odemeler: list[SalaryPaymentResponse]


class ProfitLossSummary(APIModel):
    onayli_gelir_toplami: Decimal
    onayli_gider_toplami: Decimal
    net_sonuc: Decimal
    bekleyen_gider_sayisi: int
    bekleyen_gelir_sayisi: int
