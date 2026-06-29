from decimal import Decimal

from pydantic import Field

from backend.app.models.enums import AracDurumu
from backend.app.schemas.common import APIModel


class VehicleCreate(APIModel):
    plaka: str
    tip: str
    kapasite_kg: int


class VehicleUpdate(APIModel):
    tip: str | None = None
    kapasite_kg: int | None = None
    durum: AracDurumu | None = None


class VehicleResponse(APIModel):
    id: int
    plaka: str
    tip: str
    kapasite_kg: int
    durum: AracDurumu


class VehicleScrapSaleRequest(APIModel):
    satis_tutari: Decimal = Field(ge=0)
    aciklama: str | None = None


class VehicleScrapSaleResponse(APIModel):
    arac: VehicleResponse
    gelir_kaydi_id: int
    mesaj: str


class VehicleListResponse(APIModel):
    toplam: int
    araclar: list[VehicleResponse]
