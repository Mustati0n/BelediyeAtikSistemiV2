from datetime import datetime
from decimal import Decimal

from pydantic import Field

from backend.app.models.enums import (
    GorevDurumu,
    GorevSonucu,
    GorevTipi,
    IhbarDurumu,
    KonteynerDurumu,
)
from backend.app.schemas.common import APIModel


class CitizenReportCreate(APIModel):
    aciklama: str = Field(min_length=5, max_length=2000)
    enlem: Decimal
    boylam: Decimal
    fotograf_url: str | None = Field(default=None, max_length=500)


class CitizenReportResponse(APIModel):
    ihbar_id: int
    gorev_id: int
    durum: IhbarDurumu
    mesaj: str


class ContainerFillUpdateRequest(APIModel):
    doluluk_orani: int = Field(ge=0, le=100)


class ContainerFillUpdateResponse(APIModel):
    konteyner_id: int
    doluluk_orani: int
    durum: KonteynerDurumu
    gorev_olusturuldu: bool
    gorev_id: int | None = None


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


class DriverTaskSummary(APIModel):
    id: int
    tip: GorevTipi
    durum: GorevDurumu
    oncelik: int
    planlanan_tarih: datetime | None
    sira_no: int | None
    aciklama: str | None
    kullanilan_arac_id: int | None
    kaynak: TaskSourceSummary


class DriverTaskListResponse(APIModel):
    toplam: int
    gorevler: list[DriverTaskSummary]
