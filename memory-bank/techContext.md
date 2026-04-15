# Tech Context

## Secilen Teknolojiler

- Masaustu personel ekranlari: PySide6 + QtWidgets.
- Backend/API: FastAPI.
- Vatandas web portali: FastAPI + Jinja2.
- ORM: SQLAlchemy 2.0.
- Veritabani: PostgreSQL.
- Auth: JWT.
- Harita bileseni: web tarafinda Leaflet onerilir; masaustu tarafinda gerekirse Qt WebEngine veya basit liste/koordinat tabanli MVP.
- Test: pytest, httpx test client.
- Migrasyon: Alembic.
- Yerel servisler: Docker Compose ile PostgreSQL.

## Gelistirme Ortami

- CWD: `/home/mustati0n/code-blocks/BelediyeAtikSistemi`
- Sistem tarihi: 2026-04-15
- Zaman dilimi: Europe/Istanbul
- Repo su an iskeletsiz; proje yapisi kurulacak.
- Git deposu kullanilacak; yerel commit'ler proje fazlarina gore atilacak. Push islemi yalnizca uzak repo tanimlandiktan sonra yapilabilir.

## Onerilen Klasor Yapisi

```text
backend/
  app/
    api/
    core/
    db/
    models/
    schemas/
    services/
    templates/
    static/
  alembic/
  tests/
desktop/
  app/
  ui/
docs/
memory-bank/
```

## Frontend Sonradan Eklenecegi Icin API Kurallari

- Endpoint'ler rapordaki UI ekran listesine gore adlandirilacak ve ayrilacak.
- Backend response'lari ekranlarda kullanilacak baslik, durum, tarih, tutar, iliskili varlik ozeti gibi bilgileri dogrudan tasiyacak.
- Pydantic schema'lari frontend icin sozlesme kabul edilecek.
- Backend servisleri UI framework'unden bagimsiz olacak; PySide6, Jinja2 veya ileride React/Vue gibi bir frontend ayni API'yi kullanabilecek.

## Teknik Kisitlar

- MVP'de gercek IoT sensor yok; arka plan simulasyonu kullanilacak.
- MVP'de harici banka/odeme sistemi yok.
- Rota optimizasyonu ileri algoritma degil; oncelik ve siralama tabanli basit planlama ile baslayacak.
- Vatandas tarafi uyeliksiz olacak.
- Toplu maas odemesi ayin 15'i kuralina bagli olacak.

## Kurulumda Beklenenler

- Python sanal ortam veya proje yoneticisi secilecek.
- PostgreSQL Docker Compose ile calistirilacak.
- `.env` ile veritabani, JWT secret ve uygulama ayarlari tasinacak.
- Ilk seed verileri: roller, demo personeller, araclar, bolgeler, konteynerler ve sistem parametreleri.
