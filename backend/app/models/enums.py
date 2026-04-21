from enum import StrEnum


class AracDurumu(StrEnum):
    AKTIF = "Aktif"
    PASIF = "Pasif"
    BAKIMDA = "Bakimda"


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
