from backend.app.schemas.common import APIModel


class SystemParameterResponse(APIModel):
    id: int
    anahtar: str
    deger: str
    veri_tipi: str
    kategori: str | None
    aciklama: str | None


class SystemParameterUpdate(APIModel):
    deger: str


class SystemParameterListResponse(APIModel):
    toplam: int
    parametreler: list[SystemParameterResponse]
