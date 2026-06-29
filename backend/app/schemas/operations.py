from datetime import datetime
from decimal import Decimal

from pydantic import Field, model_validator

from backend.app.models.enums import (
    GorevDurumu,
    GorevSonucu,
    GorevTipi,
    IhbarDurumu,
    KonteynerDurumu,
)
from backend.app.schemas.common import APIModel

GAZIANTEP_MIN_LAT = Decimal("36.45")
GAZIANTEP_MAX_LAT = Decimal("37.65")
GAZIANTEP_MIN_LNG = Decimal("36.55")
GAZIANTEP_MAX_LNG = Decimal("38.45")


class CitizenReportCreate(APIModel):
    aciklama: str = Field(min_length=5, max_length=2000)
    enlem: Decimal
    boylam: Decimal
    fotograf_url: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_municipality_area(self) -> "CitizenReportCreate":
        if not (
            GAZIANTEP_MIN_LAT <= self.enlem <= GAZIANTEP_MAX_LAT
            and GAZIANTEP_MIN_LNG <= self.boylam <= GAZIANTEP_MAX_LNG
        ):
            raise ValueError("Ihbar konumu Gaziantep il sinirlari icinde olmalidir.")
        return self


class CitizenReportResponse(APIModel):
    ihbar_id: int
    gorev_id: int
    durum: IhbarDurumu
    mesaj: str


class CitizenPhotoUploadResponse(APIModel):
    fotograf_url: str
    dosya_adi: str
    boyut: int


class CitizenReportStatusResponse(APIModel):
    ihbar_id: int
    durum: IhbarDurumu
    aciklama: str
    enlem: Decimal
    boylam: Decimal
    olusturma_tarihi: datetime
    gorev_id: int | None = None
    gorev_durumu: GorevDurumu | None = None


class ContainerFillUpdateRequest(APIModel):
    doluluk_orani: int = Field(ge=0, le=100)


class ContainerFillUpdateResponse(APIModel):
    konteyner_id: int
    doluluk_orani: int
    durum: KonteynerDurumu
    gorev_olusturuldu: bool
    gorev_id: int | None = None


class ContainerFillSimulationItem(APIModel):
    konteyner_id: int
    kod: str
    eski_doluluk_orani: int
    yeni_doluluk_orani: int
    artis_orani: int
    durum: KonteynerDurumu
    gorev_olusturuldu: bool
    gorev_id: int | None = None


class ContainerFillSimulationResponse(APIModel):
    toplam_konteyner: int
    guncellenen_konteyner: int
    olusan_gorev_sayisi: int
    sonuclar: list[ContainerFillSimulationItem]


class TaskAssignRequest(APIModel):
    sofor_id: int
    arac_id: int | None = None
    planlanan_tarih: datetime | None = None
    sira_no: int | None = Field(default=None, ge=1)


class TaskStartResponse(APIModel):
    gorev_id: int
    durum: GorevDurumu
    mesaj: str


class TaskCompleteRequest(APIModel):
    sonuc: GorevSonucu
    aciklama: str | None = Field(default=None, max_length=2000)


class TaskSourceSummary(APIModel):
    tip: str
    id: int
    aciklama: str
    enlem: Decimal
    boylam: Decimal
    durum: str
    doluluk_orani: int | None = None
    fotograf_url: str | None = None


class DriverVehicleSummary(APIModel):
    id: int
    plaka: str
    tip: str
    kapasite_kg: int
    durum: str


class DriverTaskSummary(APIModel):
    id: int
    tip: GorevTipi
    durum: GorevDurumu
    oncelik: int
    planlanan_tarih: datetime | None
    sira_no: int | None
    aciklama: str | None
    kullanilan_arac_id: int | None
    kullanilan_arac: DriverVehicleSummary | None = None
    kaynak: TaskSourceSummary


class DriverTaskListResponse(APIModel):
    toplam: int
    gorevler: list[DriverTaskSummary]
