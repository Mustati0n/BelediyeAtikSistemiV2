# Belediye Atık Sistemi

Akıllı şehir atık yönetimi, saha görevleri, bakım, muhasebe ve geri dönüşüm tesis süreçlerini tek sistemde birleştiren web tabanlı MVP projesidir.

## Proje Özeti

Bu proje, belediye seviyesinde atık toplama ve yönetim operasyonlarını desteklemek amacıyla geliştirilmiştir. Sistem şu alanlarda iş akışı sunar:

- Vatandaş ihbarı ve görev havuzu
- Admin denetim merkezi ve operasyon takibi
- Sürücü rota ve görev yönetimi
- Bakım kayıtları ve teknik tamamlanma akışı
- Muhasebe, gelir-gider onayı ve bordro desteği
- Geri dönüşüm teslimi, ayırıştırma, stok ve satış akışı

## Mevcut Durum

Proje şu anda çalışan bir web-first MVP olarak sunulmaktadır.

- Backend: FastAPI, SQLAlchemy 2.x, PostgreSQL, Alembic
- Web panel: React, TypeScript, Vite
- Harita/rota: Leaflet, OpenStreetMap, OSRM
- Test durumu: backend test paketi 44 passed
- Web build durumu: production build başarıyla çalışır

## Ana Özellikler

- Vatandaş ihbar portalı: konum seçimi, harita, fotoğraf yükleme, ihbar durumu sorgulama
- Admin dashboard: KPI, operasyon özeti, finans görünümü, son log kayıtları
- Filo ve personel yönetimi: araç, personel, rol ve konteyner takibi
- Operasyon akışı: görev havuzu, görev atama, başlatma ve sonuçlandırma
- Bakım yönetimi: bakım kartları, maliyet takibi ve teknik tamamlama
- Muhasebe: bekleyen gelir/gider, bordro, maaş ve raporlama
- Geri dönüşüm tesisi: teslim onayı, ayırıştırma, stok ve satış

## Teknoloji Stack

- Backend: Python, FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL, JWT
- Frontend: React, TypeScript, Vite
- Harita: Leaflet, OpenStreetMap, OSRM
- İşletim/dağıtım: Docker Compose, Nginx, HTTPS (self-signed demo ortamı)

## Kurulum

### 1) Gereksinimler

- Python 3.12+
- Node.js 20+
- Docker Compose
- npm

### 2) Depoyu klonlayın

```bash
git clone https://github.com/Mustati0n/BelediyeAtikSistemiV2.git
cd BelediyeAtikSistemi
```

### 3) Ortam değişkenlerini ayarlayın

```bash
cp .env.example .env
```

Varsayılan değerler yerelde çalışmaya uygundur. Gerekirse `.env` dosyasını düzenleyin.

### 4) Veritabanını başlatın

```bash
docker compose up -d db
```

### 5) Python ortamını oluşturun ve bağımlılıkları yükleyin

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 6) Veritabanı migrasyonlarını uygulayın

```bash
.venv/bin/alembic upgrade head
```

### 7) Demo verileri ekleyin

```bash
.venv/bin/python -m backend.app.db.seed
```

### 8) Backend'i çalıştırın

```bash
.venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

Backend şu adreste erişilebilir:

- Health: http://localhost:8000/api/v1/health
- API docs: http://localhost:8000/docs

### 9) Frontend'i çalıştırın

```bash
cd web
npm install
npm run dev
```

Web arayüzü şu adreste açılır:

- http://localhost:5173

## Demo Kullanıcıları

| Rol | E-posta | Şifre | Ana ekran |
| --- | --- | --- | --- |
| Sistem Yoneticisi | admin@belediye.local | Admin123! | /admin |
| Soför | sofor@belediye.local | Sofor123! | /driver/gorevler |
| Bakım Teknisyeni | bakim@belediye.local | Bakim123! | /maintenance/bakim |
| Muhasebe Personeli | muhasebe@belediye.local | Muhasebe123! | /finance/muhasebe |
| Geri Dönüşüm Operatörü | operator@belediye.local | Operator123! | /recycling/tesis |

## Testler

Backend testlerini çalıştırmak için:

```bash
.venv/bin/pytest
```

Web build'i doğrulamak için:

```bash
cd web
npm run build
```

## Canlı / Demo Adresler

- Personel paneli: http://77.83.37.48
- Vatandaş ihbar portalı: http://77.83.37.48/ihbar
- Backend API: http://77.83.37.48:8000/api/v1
- HTTPS deneme: https://77.83.37.48

> HTTPS tarafında self-signed sertifika kullanıldığı için tarayıcı ilk açılışta uyarı gösterebilir.

## Proje Yapısı

- backend/app: FastAPI uygulaması, endpoint'ler, servis katmanları, modeller ve şemalar
- backend/tests: pytest testleri
- web/src: React arayüzü ve sayfa bileşenleri
- docs: kullanım kılavuzu, sunum planı ve API endpoint listesi

## Dokümantasyon

- Kullanım kılavuzu: docs/kullanim-kilavuzu.md
- API endpoint listesi: docs/api-endpoint-listesi.md
- Sunum ve test planı: docs/sunum-test-plani.md
- Web portal planı: docs/web-portal-plan.md

## Katkı ve Geliştirme Notu

Bu proje bir demo / MVP kapsamındadır. Yeni özellikler eklenirken backend, frontend ve yetki akışları birlikte test edilmelidir. İleride daha kapsamlı üretim ortamı için güvenlik, CI/CD ve ortam tabanlı yapılandırma eklenmesi önerilir.
