from decimal import Decimal

from pydantic import Field

from backend.app.models.enums import KonteynerDurumu
from backend.app.schemas.common import APIModel


class RegionCreate(APIModel):
    ad: str = Field(min_length=2, max_length=150)
    aciklama: str | None = None


class RegionResponse(APIModel):
    id: int
    ad: str
    aciklama: str | None = None


class ContainerCreate(APIModel):
    kod: str = Field(min_length=2, max_length=100)
    enlem: Decimal
    boylam: Decimal
    doluluk_orani: int = Field(default=0, ge=0, le=100)
    durum: KonteynerDurumu = KonteynerDurumu.NORMAL
    bolge_id: int


class ContainerUpdate(APIModel):
    kod: str | None = Field(default=None, min_length=2, max_length=100)
    enlem: Decimal | None = None
    boylam: Decimal | None = None
    doluluk_orani: int | None = Field(default=None, ge=0, le=100)
    durum: KonteynerDurumu | None = None
    bolge_id: int | None = None


class ContainerResponse(APIModel):
    id: int
    kod: str
    enlem: Decimal
    boylam: Decimal
    doluluk_orani: int
    durum: KonteynerDurumu
    bolge: RegionResponse


class ContainerListResponse(APIModel):
    toplam: int
    konteynerler: list[ContainerResponse]
