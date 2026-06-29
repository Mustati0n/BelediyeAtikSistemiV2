from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.security import get_password_hash
from backend.app.db.session import SessionLocal
from backend.app.models.entities import (
    Arac,
    BakimKaydi,
    Bolge,
    GelirKaydi,
    GiderKaydi,
    Gorev,
    Konteyner,
    Personel,
    Rol,
    Satis,
    Stok,
    StokHareketi,
    TesisTeslim,
)
from backend.app.models.enums import (
    AracDurumu,
    AtikTipi,
    BakimDurumu,
    GorevDurumu,
    GorevTipi,
    KonteynerDurumu,
    OnayDurumu,
)
from backend.app.services.settings import ensure_default_parameters

ROLE_NAMES = [
    ("Sistem Yoneticisi", "Tum sistem yonetim yetkileri."),
    ("Muhasebe Personeli", "Maas, gider, gelir ve rapor yonetimi."),
    ("Bakim Teknisyeni", "Arac bakim ve ariza surecleri."),
    ("Sofor", "Saha operasyon gorevleri."),
    ("Geri Donusum Operatoru", "Tesis teslim, stok ve satis islemleri."),
]

UTC = timezone.utc  # noqa: UP017 - production runtime is Python 3.10.


def seed_roles_and_demo_users() -> None:
    with SessionLocal() as db:
        roles = ensure_roles(db)
        users = ensure_demo_users(db, roles)
        ensure_demo_operational_data(db, users)
        ensure_default_parameters(db)
        db.commit()


def ensure_roles(db: Session) -> dict[str, Rol]:
    roles: dict[str, Rol] = {}
    for role_name, description in ROLE_NAMES:
        stmt = select(Rol).where(Rol.ad == role_name)
        role = db.scalar(stmt)
        if role is None:
            role = Rol(ad=role_name, aciklama=description)
            db.add(role)
            db.flush()
        roles[role_name] = role
    return roles


def ensure_demo_users(db: Session, roles: dict[str, Rol]) -> dict[str, Personel]:
    demo_users = [
        {
            "tc_no": "10000000001",
            "ad_soyad": "Demo Admin",
            "email": "admin@belediye.local",
            "telefon": "5551000001",
            "taban_maas": Decimal("50000.00"),
            "cocuk_sayisi": 0,
            "rol": "Sistem Yoneticisi",
            "password": settings.seed_admin_password,
        },
        {
            "tc_no": "10000000002",
            "ad_soyad": "Demo Muhasebe",
            "email": "muhasebe@belediye.local",
            "telefon": "5551000002",
            "taban_maas": Decimal("42000.00"),
            "cocuk_sayisi": 1,
            "rol": "Muhasebe Personeli",
            "password": settings.seed_muhasebe_password,
        },
        {
            "tc_no": "10000000003",
            "ad_soyad": "Demo Bakim",
            "email": "bakim@belediye.local",
            "telefon": "5551000003",
            "taban_maas": Decimal("38000.00"),
            "cocuk_sayisi": 2,
            "rol": "Bakim Teknisyeni",
            "password": settings.seed_bakim_password,
        },
        {
            "tc_no": "10000000004",
            "ad_soyad": "Demo Sofor",
            "email": "sofor@belediye.local",
            "telefon": "5551000004",
            "taban_maas": Decimal("36000.00"),
            "cocuk_sayisi": 2,
            "rol": "Sofor",
            "password": settings.seed_sofor_password,
        },
        {
            "tc_no": "10000000005",
            "ad_soyad": "Demo Operator",
            "email": "operator@belediye.local",
            "telefon": "5551000005",
            "taban_maas": Decimal("35000.00"),
            "cocuk_sayisi": 0,
            "rol": "Geri Donusum Operatoru",
            "password": settings.seed_operator_password,
        },
    ]

    users: dict[str, Personel] = {}
    for demo_user in demo_users:
        stmt = select(Personel).where(Personel.email == demo_user["email"])
        personel = db.scalar(stmt)
        if personel is None:
            personel = Personel(
                tc_no=demo_user["tc_no"],
                sifre_hash=get_password_hash(demo_user["password"]),
                ad_soyad=demo_user["ad_soyad"],
                email=demo_user["email"],
                telefon=demo_user["telefon"],
                taban_maas=demo_user["taban_maas"],
                cocuk_sayisi=demo_user["cocuk_sayisi"],
                aktif_mi=True,
                rol=roles[demo_user["rol"]],
            )
            db.add(personel)
            db.flush()
        users[demo_user["rol"]] = personel
    return users


def ensure_demo_operational_data(db: Session, users: dict[str, Personel]) -> None:
    bolgeler = ensure_demo_regions(db)
    araclar = ensure_demo_vehicles(db)
    konteynerler = ensure_demo_containers(db, bolgeler)
    ensure_demo_open_task(db, konteynerler["GZP-003"])
    ensure_demo_maintenance(db, araclar["27ATK002"], users["Bakim Teknisyeni"])
    ensure_demo_recycling_flow(db, users["Sofor"], users["Geri Donusum Operatoru"])


def ensure_demo_regions(db: Session) -> dict[str, Bolge]:
    demo_regions = {
        "Sahinbey": "Gaziantep Sahinbey merkez ve yakin mahalleler.",
        "Sehitkamil": "Gaziantep Sehitkamil park ve konut akslari.",
        "Organize Sanayi": "Gaziantep organize sanayi ve lojistik akslari.",
    }
    regions: dict[str, Bolge] = {}
    for name, description in demo_regions.items():
        region = db.scalar(select(Bolge).where(Bolge.ad == name))
        if region is None:
            region = Bolge(ad=name, aciklama=description)
            db.add(region)
            db.flush()
        else:
            region.aciklama = description
        regions[name] = region
    return regions


def ensure_demo_vehicles(db: Session) -> dict[str, Arac]:
    demo_vehicles = [
        ("27ATK001", "34ATK001", "Sikistirmali Cop Kamyonu", 12000, AracDurumu.AKTIF),
        ("27ATK002", "34ATK002", "Konteyner Yikama Araci", 6500, AracDurumu.BAKIMDA),
        ("27ATK003", "34ATK003", "Geri Donusum Kamyonu", 9000, AracDurumu.AKTIF),
    ]
    vehicles: dict[str, Arac] = {}
    for plate, legacy_plate, vehicle_type, capacity, status in demo_vehicles:
        vehicle = db.scalar(select(Arac).where(Arac.plaka == plate))
        if vehicle is None:
            vehicle = db.scalar(select(Arac).where(Arac.plaka == legacy_plate))
        if vehicle is None:
            vehicle = Arac(plaka=plate, tip=vehicle_type, kapasite_kg=capacity, durum=status)
            db.add(vehicle)
            db.flush()
        else:
            vehicle.plaka = plate
            vehicle.tip = vehicle_type
            vehicle.kapasite_kg = capacity
        vehicles[plate] = vehicle
    return vehicles


def ensure_demo_containers(db: Session, regions: dict[str, Bolge]) -> dict[str, Konteyner]:
    demo_containers = [
        ("GZP-001", "MER-001", "Sahinbey", "37.0662000", "37.3833000", 35, KonteynerDurumu.NORMAL),
        ("GZP-002", "SAH-001", "Sehitkamil", "37.0867000", "37.3675000", 68, KonteynerDurumu.IZLENIYOR),
        (
            "GZP-003",
            "SAN-001",
            "Organize Sanayi",
            "37.1459000",
            "37.3278000",
            92,
            KonteynerDurumu.KRITIK,
        ),
    ]
    containers: dict[str, Konteyner] = {}
    for code, legacy_code, region_name, lat, lng, fill, status_value in demo_containers:
        container = db.scalar(select(Konteyner).where(Konteyner.kod == code))
        if container is None:
            container = db.scalar(select(Konteyner).where(Konteyner.kod == legacy_code))
        if container is None:
            container = Konteyner(
                kod=code,
                enlem=Decimal(lat),
                boylam=Decimal(lng),
                doluluk_orani=fill,
                durum=status_value,
                bolge=regions[region_name],
            )
            db.add(container)
            db.flush()
        else:
            container.kod = code
            container.enlem = Decimal(lat)
            container.boylam = Decimal(lng)
            container.bolge = regions[region_name]
        containers[code] = container
    return containers


def ensure_demo_open_task(db: Session, container: Konteyner) -> None:
    existing_task = db.scalar(
        select(Gorev).where(
            Gorev.konteyner_id == container.id,
            Gorev.durum.in_([GorevDurumu.BEKLIYOR, GorevDurumu.ATANDI, GorevDurumu.ISLEMDE]),
        )
    )
    if existing_task is not None:
        return

    db.add(
        Gorev(
            tip=GorevTipi.KRITIK_KONTEYNER,
            oncelik=8,
            durum=GorevDurumu.BEKLIYOR,
            planlanan_tarih=datetime.now(UTC),
            sira_no=1,
            aciklama="Demo kritik konteyner gorevi.",
            konteyner=container,
        )
    )


def ensure_demo_maintenance(db: Session, vehicle: Arac, technician: Personel) -> None:
    existing = db.scalar(select(BakimKaydi).where(BakimKaydi.aciklama == "Demo periyodik bakim."))
    if existing is not None:
        existing.bakim_turu = existing.bakim_turu or "Periyodik"
        existing.oncelik = existing.oncelik or "Kritik"
        existing.parca_maliyeti_tl = existing.parca_maliyeti_tl or Decimal("12500.00")
        existing.iscilik_maliyeti_tl = existing.iscilik_maliyeti_tl or Decimal("6000.00")
        existing.tedarikci = existing.tedarikci or "Gaziantep Yetkili Servis"
        existing.kilometre = existing.kilometre or 182000
        existing.planlanan_tarih = existing.planlanan_tarih or datetime.now(UTC)
        return

    maintenance = BakimKaydi(
        tarih=datetime.now(UTC),
        aciklama="Demo periyodik bakim.",
        bakim_turu="Periyodik",
        oncelik="Kritik",
        maliyet_tl=Decimal("18500.00"),
        parca_maliyeti_tl=Decimal("12500.00"),
        iscilik_maliyeti_tl=Decimal("6000.00"),
        tedarikci="Gaziantep Yetkili Servis",
        kilometre=182000,
        planlanan_tarih=datetime.now(UTC),
        durum=BakimDurumu.ACILDI,
        arac=vehicle,
        olusturan_personel=technician,
    )
    db.add(maintenance)
    db.flush()
    db.add(
        GiderKaydi(
            tarih=maintenance.tarih,
            tutar=maintenance.maliyet_tl,
            aciklama=f"{vehicle.plaka} demo bakim gideri",
            durum=OnayDurumu.BEKLEMEDE,
            bakim_kaydi=maintenance,
        )
    )


def ensure_demo_recycling_flow(db: Session, driver: Personel, operator: Personel) -> None:
    waiting_delivery = db.scalar(
        select(TesisTeslim).where(TesisTeslim.aciklama == "Demo bekleyen tesis teslimi.")
    )
    if waiting_delivery is None:
        db.add(
            TesisTeslim(
                tarih=datetime.now(UTC),
                toplam_kg=Decimal("240.000"),
                aciklama="Demo bekleyen tesis teslimi.",
                onaylandi_mi=False,
                teslim_eden_sofor=driver,
            )
        )

    sorted_delivery = db.scalar(
        select(TesisTeslim).where(TesisTeslim.aciklama == "Demo onayli ayristirilmis teslim.")
    )
    if sorted_delivery is None:
        sorted_delivery = TesisTeslim(
            tarih=datetime.now(UTC),
            toplam_kg=Decimal("310.000"),
            aciklama="Demo onayli ayristirilmis teslim.",
            onaylandi_mi=True,
            onay_tarihi=datetime.now(UTC),
            teslim_eden_sofor=driver,
            teslim_alan_operator=operator,
        )
        db.add(sorted_delivery)
        db.flush()
        ensure_demo_stock_movement(
            db,
            sorted_delivery,
            AtikTipi.PLASTIK,
            Decimal("140.000"),
            "Demo plastik ayristirma.",
        )
        ensure_demo_stock_movement(
            db,
            sorted_delivery,
            AtikTipi.CAM,
            Decimal("90.000"),
            "Demo cam ayristirma.",
        )

    ensure_demo_pending_sale(db)


def ensure_demo_stock_movement(
    db: Session,
    delivery: TesisTeslim,
    waste_type: AtikTipi,
    amount: Decimal,
    description: str,
) -> None:
    stock = db.scalar(select(Stok).where(Stok.atik_tipi == waste_type))
    if stock is None:
        stock = Stok(atik_tipi=waste_type, toplam_miktar_kg=Decimal("0.000"))
        db.add(stock)
        db.flush()

    movement = db.scalar(
        select(StokHareketi).where(
            StokHareketi.tesis_teslim_id == delivery.id,
            StokHareketi.atik_tipi == waste_type,
        )
    )
    if movement is None:
        stock.toplam_miktar_kg += amount
        db.add(
            StokHareketi(
                tarih=datetime.now(UTC),
                atik_tipi=waste_type,
                miktar_kg=amount,
                aciklama=description,
                tesis_teslim=delivery,
                stok=stock,
            )
        )


def ensure_demo_pending_sale(db: Session) -> None:
    existing_sale = db.scalar(select(Satis).where(Satis.durum == OnayDurumu.BEKLEMEDE))
    if existing_sale is not None:
        return

    stock = db.scalar(select(Stok).where(Stok.atik_tipi == AtikTipi.PLASTIK))
    if stock is None:
        stock = Stok(atik_tipi=AtikTipi.PLASTIK, toplam_miktar_kg=Decimal("0.000"))
        db.add(stock)
        db.flush()
    if stock.toplam_miktar_kg < Decimal("30.000"):
        stock.toplam_miktar_kg += Decimal("30.000")

    sale = Satis(
        tarih=datetime.now(UTC),
        miktar_kg=Decimal("30.000"),
        birim_fiyat=Decimal("12.50"),
        toplam_tutar=Decimal("375.00"),
        durum=OnayDurumu.BEKLEMEDE,
        stok=stock,
    )
    db.add(sale)
    stock.toplam_miktar_kg -= sale.miktar_kg
    db.flush()
    db.add(
        GelirKaydi(
            tarih=sale.tarih,
            tutar=sale.toplam_tutar,
            aciklama="Demo plastik satis geliri",
            durum=OnayDurumu.BEKLEMEDE,
            satis=sale,
        )
    )


if __name__ == "__main__":
    seed_roles_and_demo_users()
