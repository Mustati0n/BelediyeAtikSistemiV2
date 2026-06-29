# Tech Context

## Secilen Teknolojiler

- Masaustu personel ekranlari: PySide6 + QtWidgets.
- Personel web paneli: React + Vite + TypeScript.
- Backend/API: FastAPI.
- Vatandas web portali: ayri domain/subdomain hedefli web arayuzu; teknoloji nihai olarak netlestirilecek.
- ORM: SQLAlchemy 2.0.
- Veritabani: PostgreSQL.
- Auth: JWT.
- Sifre hashleme: Passlib `pbkdf2_sha256`.
- Harita bileseni: web tarafinda Leaflet onerilir; masaustu tarafinda gerekirse Qt WebEngine veya basit liste/koordinat tabanli MVP.
- Test: pytest, httpx test client.
- Migrasyon: Alembic.
- Yerel servisler: Docker Compose ile PostgreSQL.

## Gelistirme Ortami

- CWD: `/home/mustati0n/code-blocks/BelediyeAtikSistemi`
- Guncel sunucu CWD: `/root/BelediyeAtikSistemi`
- Son dogrulanan sistem tarihi: 2026-06-11
- Zaman dilimi: Europe/Istanbul
- Repo su an iskeletsiz; proje yapisi kurulacak.
- Git deposu kullanilacak; yerel commit'ler proje fazlarina gore atilacak. Push islemi yalnizca uzak repo tanimlandiktan sonra yapilabilir.
- Faz 1 iskeleti kuruldu ve `.venv` icinde bagimlilikler yuklendi.
- Bu ortamda Docker CLI Podman ile emule ediliyor; `docker compose` komutu `podman-compose` provider'i ile calisiyor.
- Aktif Python surumu: 3.14.3.
- Sunucuda web panel icin Node.js `v20.20.2` ve npm `10.8.2` kullanildi.
- Web panel nginx ile `/var/www/belediye-atik-web` altindan yayinlaniyor.
- Backend `0.0.0.0:8000`, web panel `http://77.83.37.48`, API `http://77.83.37.48:8000/api/v1`.

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
web/
  src/
  dist/
docs/
memory-bank/
```

## Frontend Sonradan Eklenecegi Icin API Kurallari

- Endpoint'ler rapordaki UI ekran listesine gore adlandirilacak ve ayrilacak.
- Backend response'lari ekranlarda kullanilacak baslik, durum, tarih, tutar, iliskili varlik ozeti gibi bilgileri dogrudan tasiyacak.
- Pydantic schema'lari frontend icin sozlesme kabul edilecek.
- Backend servisleri UI framework'unden bagimsiz olacak; PySide6, Jinja2 veya ileride React/Vue gibi bir frontend ayni API'yi kullanabilecek.
- Gosterim icin eklenen gecici UI veya test ekranlari cekirdek servis katmanindan bagimsiz bir adapter olarak yazilacak; sonradan silinmesi backend akisini bozmamali.

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
- Mevcut seed betigi su an roller ve demo personelleri olusturur: `python -m backend.app.db.seed`.

## Faz 1 Dogrulama

- `.venv/bin/python -m pytest`: 2 test gecti.
- `.venv/bin/python -m ruff check .`: gecti.
- `python3 -m compileall backend`: gecti.
- `docker compose config`: gecti.

## Faz 2 Dogrulama

- `.venv/bin/python -m pytest`: 5 test gecti.
- `.venv/bin/python -m ruff check backend`: gecti.
- `python3 -m compileall backend`: gecti.
- `.venv/bin/alembic revision --autogenerate -m "create initial schema"`: gecti.
- `.venv/bin/alembic upgrade head`: gecti.
- `.venv/bin/alembic current`: `00f31c245a1a (head)`.
- `.venv/bin/alembic check`: `No new upgrade operations detected.`

## Faz 3 Dogrulama

- `.venv/bin/python -m ruff check backend`: gecti.
- `.venv/bin/python -m pytest`: 9 test gecti.
- `python3 -m compileall backend`: gecti.
- `.venv/bin/python -m backend.app.db.seed`: gecti.

## Faz 4 Dogrulama

- `.venv/bin/python -m ruff check backend`: gecti.
- `.venv/bin/python -m pytest`: 13 test gecti.
- `python3 -m compileall backend`: gecti.

## Faz 5 Dogrulama

- `.venv/bin/python -m ruff check backend`: gecti.
- `.venv/bin/python -m pytest`: 18 test gecti.
- `python3 -m compileall backend`: gecti.

## Faz 6 Dogrulama

- `.venv/bin/python -m ruff check backend`: gecti.
- `.venv/bin/python -m pytest`: 22 test gecti.
- `python3 -m compileall backend`: gecti.

## Faz 7 Web Dogrulama

- `.venv/bin/pytest`: 28 test gecti.
- `npm run build`: gecti.
- `nginx -t`: gecti.
- `curl http://77.83.37.48:8000/api/v1/health`: `{"status":"ok","service":"backend"}`.
- `http://77.83.37.48/admin/filo`, `/admin/personel`, `/admin/konteynerler`, `/admin/gorevler`, `/driver/gorevler` nginx uzerinden 200 donuyor.
- `http://77.83.37.48/maintenance/bakim` nginx uzerinden 200 donuyor.
- `GET /api/v1/maintenance/bakim-kayitlari` bakim kullanicisi ile canli veritabaninda dogrulandi.
- `http://77.83.37.48/finance/muhasebe` nginx uzerinden 200 donuyor.
- Muhasebe kullanicisiyle bekleyen gider, bekleyen gelir ve kar-zarar endpoint'leri canli veritabaninda dogrulandi.
- `http://77.83.37.48/recycling/tesis` nginx uzerinden 200 donuyor.
- Operator kullanicisiyle teslim listeleme ve stok listeleme endpoint'leri canli veritabaninda dogrulandi.
- `http://77.83.37.48/ihbar` nginx uzerinden 200 donuyor.
- Public ihbar endpoint'i test edildi; olusan ihbar admin gorev havuzunda goruldu.
- Rol bazli frontend guard build edildi ve nginx'e yayinlandi. `npm run build` ve `nginx -t` gecti.
