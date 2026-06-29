from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.entities import SistemParametresi
from backend.app.schemas.settings import SystemParameterListResponse

DEFAULT_PARAMETERS = [
    (
        "kritik_doluluk_esigi",
        "85",
        "integer",
        "Operasyon",
        "Konteyner dolulugu bu yuzdeye ulasinca kritik gorev uretimi tetiklenir.",
    ),
    (
        "izleme_doluluk_esigi",
        "60",
        "integer",
        "Operasyon",
        "Konteynerin izleme durumuna alinacagi doluluk yuzdesi.",
    ),
    (
        "simulasyon_min_artis",
        "5",
        "integer",
        "Simulasyon",
        "Sensor simulasyonunda uygulanacak minimum doluluk artisi.",
    ),
    (
        "simulasyon_max_artis",
        "22",
        "integer",
        "Simulasyon",
        "Sensor simulasyonunda uygulanacak maksimum doluluk artisi.",
    ),
    (
        "plastik_birim_fiyat",
        "12.50",
        "decimal",
        "Tesis",
        "Plastik stok satislarinda onerilen varsayilan birim fiyat.",
    ),
    (
        "cam_birim_fiyat",
        "4.10",
        "decimal",
        "Tesis",
        "Cam stok satislarinda onerilen varsayilan birim fiyat.",
    ),
    (
        "metal_birim_fiyat",
        "16.75",
        "decimal",
        "Tesis",
        "Metal stok satislarinda onerilen varsayilan birim fiyat.",
    ),
    (
        "kagit_birim_fiyat",
        "5.60",
        "decimal",
        "Tesis",
        "Kagit stok satislarinda onerilen varsayilan birim fiyat.",
    ),
    (
        "organik_birim_fiyat",
        "2.20",
        "decimal",
        "Tesis",
        "Organik atik stok satislarinda onerilen varsayilan birim fiyat.",
    ),
    (
        "diger_birim_fiyat",
        "1.25",
        "decimal",
        "Tesis",
        "Diger atik stok satislarinda onerilen varsayilan birim fiyat.",
    ),
    (
        "taban_maas_carpani",
        "1.20",
        "decimal",
        "Muhasebe",
        "Maas hesaplamalarinda kullanilacak kurumsal katsayi.",
    ),
    (
        "cocuk_basina_ek_odeme",
        "1000.00",
        "decimal",
        "Muhasebe",
        "Personel maas hesaplamasinda cocuk basina uygulanacak ek tutar.",
    ),
]


def ensure_default_parameters(db: Session) -> None:
    for key, value, data_type, category, description in DEFAULT_PARAMETERS:
        parameter = db.scalar(select(SistemParametresi).where(SistemParametresi.anahtar == key))
        if parameter is None:
            db.add(
                SistemParametresi(
                    anahtar=key,
                    deger=value,
                    veri_tipi=data_type,
                    kategori=category,
                    aciklama=description,
                )
            )
    db.flush()


def list_system_parameters(db: Session) -> SystemParameterListResponse:
    ensure_default_parameters(db)
    parameters = list(
        db.scalars(
            select(SistemParametresi).order_by(
                SistemParametresi.kategori.asc(),
                SistemParametresi.anahtar.asc(),
            )
        )
    )
    return SystemParameterListResponse(toplam=len(parameters), parametreler=parameters)
