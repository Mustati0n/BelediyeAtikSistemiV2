# Belediye Atik Sistemi

Akilli sehir atik yonetimi, saha gorevleri, bakim, muhasebe ve geri donusum
tesis akislarini tek sistemde gosteren okul projesi demo uygulamasi.

## Mevcut Durum

Proje calisan web tabanli MVP seviyesindedir.

- Backend: FastAPI, SQLAlchemy, PostgreSQL, Alembic
- Web panel: React, Vite, TypeScript
- Harita: Leaflet, OpenStreetMap, OSRM rota servisi
- Yayin: Nginx uzerinden statik web, FastAPI backend `8000` portunda
- Test durumu: backend test paketi `41 passed`

## Canli Adresler

- Personel paneli: `http://77.83.37.48`
- Vatandas ihbar portali: `http://77.83.37.48/ihbar`
- Alternatif vatandas portali: `http://77.83.37.48/vatandas`
- Backend API: `http://77.83.37.48:8000/api/v1`
- Backend health: `http://77.83.37.48:8000/api/v1/health`
- HTTPS deneme: `https://77.83.37.48`

HTTPS IP uzerinden self-signed sertifika ile calisir; tarayici ilk giriste uyari
gosterebilir.

## Demo Kullanici Bilgileri

| Rol | E-posta | Sifre | Ana ekran |
| --- | --- | --- | --- |
| Sistem Yoneticisi | `admin@belediye.local` | `Admin123!` | `/admin` |
| Sofor | `sofor@belediye.local` | `Sofor123!` | `/driver/gorevler` |
| Bakim Teknisyeni | `bakim@belediye.local` | `Bakim123!` | `/maintenance/bakim` |
| Muhasebe Personeli | `muhasebe@belediye.local` | `Muhasebe123!` | `/finance/muhasebe` |
| Geri Donusum Operatoru | `operator@belediye.local` | `Operator123!` | `/recycling/tesis` |

## Ana Moduller

- Vatandas ihbar portali: konum, harita, hizli test konumlari, fotograf yukleme ve ihbar durum sorgulama.
- Admin denetim merkezi: KPI, harita ozeti, finans ozeti, son loglar, sistem uyarilari.
- Admin alt sayfalari: filo, personel, konteyner, gorevler, finans, parametreler, log kayitlari.
- Sofor paneli: Gaziantep haritasi, yol bazli rota, gorev baslatma ve sonuclandirma.
- Bakim paneli: is emri, arac bakimi, maliyet detaylari, teknik tamamlama.
- Muhasebe paneli: gelir/gider onaylari, kar-zarar ozeti, bordro, personel karti ve ek kalemler.
- Geri donusum tesisi: teslim onayi, ayristirma, stok, satis, satis/stok gecmisi.

## Yerel Calistirma

Backend:

```bash
.venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

Migration:

```bash
.venv/bin/alembic upgrade head
```

Seed:

```bash
.venv/bin/python -m backend.app.db.seed
```

Backend testleri:

```bash
.venv/bin/pytest
```

Web build:

```bash
cd web
npm run build
```

## Sunum Dokumanlari

- Kullanim kilavuzu: `docs/kullanim-kilavuzu.md`
- Sunum ve manuel test plani: `docs/sunum-test-plani.md`
- Web gecis plani: `docs/web-portal-plan.md`
