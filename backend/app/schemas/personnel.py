from decimal import Decimal

from pydantic import Field, field_validator

from backend.app.schemas.common import APIModel


class RoleResponse(APIModel):
    id: int
    ad: str
    aciklama: str | None = None


class PersonnelResponse(APIModel):
    id: int
    tc_no: str
    ad_soyad: str
    email: str
    telefon: str | None = None
    taban_maas: Decimal
    cocuk_sayisi: int
    aktif_mi: bool
    rol: RoleResponse


class PersonnelListResponse(APIModel):
    toplam: int
    personeller: list[PersonnelResponse]


class PersonnelCreate(APIModel):
    tc_no: str = Field(min_length=11, max_length=11)
    ad_soyad: str = Field(min_length=2, max_length=255)
    email: str = Field(min_length=3, max_length=255)
    telefon: str | None = Field(default=None, min_length=10, max_length=11)
    taban_maas: Decimal = Field(default=Decimal("0.00"), ge=0, le=Decimal("250000.00"))
    cocuk_sayisi: int = Field(default=0, ge=0, le=10)
    rol_id: int
    password: str = Field(min_length=6, max_length=128)

    @field_validator("tc_no")
    @classmethod
    def validate_tc_no(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("TC no sadece rakamlardan olusmalidir.")
        return value

    @field_validator("ad_soyad")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if any(character.isdigit() for character in value):
            raise ValueError("Ad soyad alaninda rakam olamaz.")
        return value.strip()

    @field_validator("telefon")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        if not value.isdigit():
            raise ValueError("Telefon sadece rakamlardan olusmalidir.")
        return value


class PersonnelUpdate(APIModel):
    ad_soyad: str | None = Field(default=None, min_length=2, max_length=255)
    email: str | None = Field(default=None, min_length=3, max_length=255)
    telefon: str | None = Field(default=None, min_length=10, max_length=11)
    taban_maas: Decimal | None = Field(default=None, ge=0, le=Decimal("250000.00"))
    cocuk_sayisi: int | None = Field(default=None, ge=0, le=10)
    rol_id: int | None = None
    aktif_mi: bool | None = None
    password: str | None = Field(default=None, min_length=6, max_length=128)

    @field_validator("ad_soyad")
    @classmethod
    def validate_optional_name(cls, value: str | None) -> str | None:
        if value is not None and any(character.isdigit() for character in value):
            raise ValueError("Ad soyad alaninda rakam olamaz.")
        return value.strip() if value is not None else None

    @field_validator("telefon")
    @classmethod
    def validate_optional_phone(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        if not value.isdigit():
            raise ValueError("Telefon sadece rakamlardan olusmalidir.")
        return value
