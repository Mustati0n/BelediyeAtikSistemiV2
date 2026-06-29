try:
    from enum import StrEnum
except ImportError:
    # Python 3.10 compatibility - StrEnum was added in Python 3.11
    from enum import Enum

    class StrEnum(str, Enum):
        def _generate_next_value_(name, start, count, last_values):
            return name.lower()

        def __str__(self) -> str:
            return str(self.value)


class AracDurumu(StrEnum):
    AKTIF = "Aktif"
    PASIF = "Pasif"
    BAKIMDA = "Bakimda"
    HURDA = "Hurda"


class KonteynerDurumu(StrEnum):
    NORMAL = "Normal"
    IZLENIYOR = "Izleniyor"
    KRITIK = "Kritik"
    GOREVE_ATANDI = "GoreveAtandi"
    BOSALTILDI = "Bosaltildi"


class IhbarDurumu(StrEnum):
    BEKLIYOR = "Bekliyor"
    GOREVE_ATANDI = "GoreveAtandi"
    ISLEMDE = "Islemde"
    COZULDU = "Cozuldu"
    GECERSIZ = "Gecersiz"


class GorevTipi(StrEnum):
    IHBAR = "Ihbar"
    KRITIK_KONTEYNER = "KritikKonteyner"


class GorevDurumu(StrEnum):
    BEKLIYOR = "Bekliyor"
    ATANDI = "Atandi"
    ISLEMDE = "Islemde"
    TAMAMLANDI = "Tamamlandi"
    BASARISIZ = "Basarisiz"


class GorevSonucu(StrEnum):
    TAMAMLANDI = "Tamamlandi"
    ULASILAMADI = "Ulasilamadi"
    YANLIS_IHBAR = "YanlisIhbar"
    TEKRAR_KONTROL_GEREKLI = "TekrarKontrolGerekli"


class AtikTipi(StrEnum):
    PLASTIK = "Plastik"
    CAM = "Cam"
    METAL = "Metal"
    KAGIT = "Kagit"
    ORGANIK = "Organik"
    DIGER = "Diger"


class BakimDurumu(StrEnum):
    ACILDI = "Acildi"
    INCELEMEDE = "Incelemede"
    TAMAMLANDI = "Tamamlandi"
    IPTAL = "Iptal"


class OnayDurumu(StrEnum):
    BEKLEMEDE = "Beklemede"
    ONAYLANDI = "Onaylandi"
    REDDEDILDI = "Reddedildi"


class OdemeTipi(StrEnum):
    AVANS = "Avans"
    TEKLI = "Tekli"
    TOPLU = "Toplu"


class OdemeDurumu(StrEnum):
    BEKLIYOR = "Bekliyor"
    ODENDI = "Odendi"
    IPTAL = "Iptal"
