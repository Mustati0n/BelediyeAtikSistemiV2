# Web Portal Gecis Plani

## Hedef

Masaustu PySide6 arayuzundeki mevcut tasarim dilini koruyarak sistemi web'e tasimak.
Personel sistemi rol bazli tek yonetim paneli olarak calisir. Okul projesi demo ortaminda
domain alinmayacagi icin vatandas ihbar portali ayni IP uzerinde ayri URL ile sunulur.

## Sunucu Durumu

- Backend: `http://77.83.37.48:8000/api/v1`
- Backend health: `/api/v1/health`
- Node.js: `v20.20.2`
- npm: `10.8.2`
- Nginx: aktif, 80 portunda dinliyor
- Backend sureci: `0.0.0.0:8000`

## Demo URL Yapisi

- Panel: `http://77.83.37.48`
- Vatandas portali: `http://77.83.37.48/vatandas`
- Alternatif vatandas portali: `http://77.83.37.48/ihbar`
- API: `http://77.83.37.48:8000/api/v1`

## Teknoloji Secimi

Oneri: React + Vite + TypeScript

Gerekce:

- Mevcut FastAPI backend ile temiz API entegrasyonu yapar.
- Build cikisi statik dosya olarak nginx ile kolay yayinlanir.
- Personel paneli ve vatandas portali ayni repo icinde ayrilabilir.
- Mevcut masaustu UI tasarimina benzer kart, tablo ve panel yapilari rahat uygulanir.

## Faz 1: Web Temel Iskelet

1. `web/` klasoru olustur.
2. React + Vite + TypeScript kur.
3. Ortak API client yaz.
4. Auth token saklama ve cikis akisi ekle.
5. Rol bazli route guard yap.
6. Ortak layout bilesenleri olustur:
   - Login layout
   - Panel layout
   - Sidebar
   - Header
   - Card
   - Table
   - Status badge
   - Modal
   - Toast/alert

## Faz 2: Ortak Personel Login

Sayfa: `/login`

Icerik:

- Kullanici adi/e-posta alani
- Sifre alani
- Giris butonu
- Hata mesaji
- Backend baglanti durumu
- Basarili giris sonrasi role gore yonlendirme

Rol yonlendirme:

- `Sistem Yoneticisi` -> `/admin`
- `Sofor` -> `/driver/gorevler`
- `Bakim Teknisyeni` -> `/maintenance/bakim`
- `Muhasebe Personeli` -> `/finance/muhasebe`
- `Geri Donusum Operatoru` -> `/recycling/tesis`

## Faz 3: Sistem Yoneticisi Sayfalari

### 3.1 Admin Dashboard

Route: `/admin`

Icerik:

- Gunluk toplanan atik miktari
- Aktif arac sayisi
- Bakimda arac sayisi
- Bekleyen ihbar sayisi
- Kritik doluluk alarmi sayisi
- Bekleyen gelir/gider onay sayilari
- Aylik gelir-gider ozeti
- Grafik ve ozet kartlari

Backend ihtiyaci:

- Dashboard summary endpoint'i eklenecek.

### 3.2 Personel ve Rol Yonetimi

Route: `/admin/personel`

Icerik:

- Personel listesi
- Arama ve filtreleme
- Yeni personel ekleme
- Personel guncelleme
- Rol atama
- Aktif/pasif yapma

Backend ihtiyaci:

- Personel listeleme
- Personel olusturma
- Personel guncelleme
- Personel aktif/pasif guncelleme
- Rol listeleme

### 3.3 Arac ve Filo Yonetimi

Route: `/admin/filo`

Icerik:

- Arac listesi
- Plaka, tip, kapasite, durum
- Yeni arac ekleme
- Arac guncelleme
- Aktif/pasif/bakimda durumu

Backend durumu:

- Mevcut endpoint'ler var: `/fleet/araclar`

### 3.4 Bolge ve Konteyner Yonetimi

Route: `/admin/konteynerler`

Icerik:

- Harita alani
- Konteyner pinleri
- Yeni konteyner ekleme
- Konteyner guncelleme/silme
- Bolge atama
- Doluluk ve durum bilgisi

Backend ihtiyaci:

- Konteyner listeleme
- Konteyner olusturma
- Konteyner guncelleme
- Bolge listeleme/olusturma
- Harita koordinat alanlari netlestirme

### 3.5 Sistem Parametreleri

Route: `/admin/parametreler`

Icerik:

- Kritik doluluk esigi
- Cocuk basi ek odeme
- Maas katsayilari
- Atik turu birim fiyatlari
- Diger esik ve katsayilar

Backend ihtiyaci:

- Parametre listeleme
- Parametre guncelleme

### 3.6 Audit Log

Route: `/admin/audit-log`

Icerik:

- Islem tarihi
- Kullanici
- Islem tipi
- Aciklama
- Varlik tipi/id
- Tarih ve kullanici filtreleri

Backend ihtiyaci:

- Audit log listeleme endpoint'i
- Filtre parametreleri

## Faz 4: Sofor Sayfalari

### 4.1 Vardiya ve Arac

Route: `/driver/vardiya`

Icerik:

- Sofor bilgisi
- Atanmis arac
- Plaka ve kapasite
- Vardiyayi baslat
- Gunluk rotayi getir

Backend durumu:

- Sofor gorev listesi endpoint'i mevcut.
- Vardiya baslat/kapat icin gerekirse yeni endpoint eklenecek.

### 4.2 Gunluk Gorev ve Rota

Route: `/driver/gorevler`

Icerik:

- Harita
- Gorev pinleri
- Gorev listesi
- Oncelik, tip ve durum bilgisi
- Gorevi baslat
- Gorevi tamamla
- Sorunlu/basarisiz isaretle

Backend durumu:

- Gorev listeleme, baslatma ve sonuclandirma endpoint'leri mevcut.

### 4.3 Gorev Sonuclandirma

UI: modal/popup

Icerik:

- Tamamlandi
- Ulasilamadi
- Yanlis ihbar
- Tekrar kontrol gerekli
- Aciklama
- Kaydet

Backend durumu:

- Sonuclandirma endpoint'i mevcut.

### 4.4 Tesise Teslim

Route: `/driver/teslim`

Icerik:

- Toplam kg
- Aciklama
- Tesise teslim et
- Vardiyayi kapat

Backend durumu:

- Teslim endpoint'i mevcut: `/recycling/teslimler`

## Faz 5: Bakim Teknisyeni Sayfalari

### 5.1 Arac Listesi ve Durum

Route: `/maintenance/araclar`

Icerik:

- Arac listesi
- Plaka, tip, durum
- Arama/filtre

Backend durumu:

- `/fleet/araclar` bakim rolune acik.

### 5.2 Bakim Kaydi Olusturma

Route: `/maintenance/kayit-olustur`

Icerik:

- Arac secimi
- Tarih
- Aciklama
- Maliyet
- Kayit olustur

Backend durumu:

- `/maintenance/bakim-kayitlari` mevcut.

### 5.3 Bakim Gecmisi

Route: `/maintenance/gecmis`

Icerik:

- Arac bazli bakim kayitlari
- Tarih, aciklama, maliyet
- Teknik durum
- Gider onay durumu

Backend ihtiyaci:

- Bakim kayitlari listeleme endpoint'i eklenecek.

## Faz 6: Muhasebe Sayfalari

### 6.1 Maas Yonetimi

Route: `/finance/maas`

Icerik:

- Personel listesi
- Maas hesaplama
- Tekli odeme/avans
- Toplu maas ode
- Odeme durumu

Backend durumu:

- Maas hesaplama, tekli ve toplu odeme endpoint'leri mevcut.
- Personel listesi endpoint'i gerekecek.

### 6.2 Gider Onay

Route: `/finance/giderler`

Icerik:

- Bekleyen giderler
- Tutar, aciklama, tarih
- Arac/bakim bilgisi
- Onayla/reddet

Backend durumu:

- Bekleyen gider, onay ve red endpoint'leri mevcut.

### 6.3 Gelir Onay

Route: `/finance/gelirler`

Icerik:

- Bekleyen gelirler
- Satis bilgisi
- Tutar
- Onayla/reddet

Backend durumu:

- Bekleyen gelir, onay ve red endpoint'leri mevcut.

### 6.4 Finansal Raporlar

Route: `/finance/raporlar`

Icerik:

- Gelir toplam
- Gider toplam
- Net kar/zarar
- Grafik
- Donem filtresi

Backend durumu:

- Kar-zarar endpoint'i mevcut.
- Donem filtresi gerekirse genisletilecek.

## Faz 7: Geri Donusum Operatoru Sayfalari

### 7.1 Teslim Alma

Route: `/recycling/teslimler`

Icerik:

- Bekleyen teslimler
- Sofor bilgisi
- Teslim tarihi
- Toplam kg
- Teslimi onayla

Backend ihtiyaci:

- Bekleyen teslim listeleme endpoint'i eklenecek.
- Onay endpoint'i mevcut.

### 7.2 Ayristirma ve Stok Girisi

Route: `/recycling/ayristirma`

Icerik:

- Teslim secimi
- Atik turu
- Kg girisi
- Stoka ekle

Backend durumu:

- Ayristirma endpoint'i mevcut.

### 7.3 Stok Goruntuleme

Route: `/recycling/stoklar`

Icerik:

- Atik turu
- Toplam miktar
- Son hareket tarihi
- Filtre

Backend durumu:

- Stok listeleme endpoint'i mevcut.

### 7.4 Satis Olusturma

Route: `/recycling/satis`

Icerik:

- Atik turu
- Miktar
- Birim fiyat
- Toplam tutar
- Satis kaydi olustur

Backend durumu:

- Satis endpoint'i mevcut.

## Faz 8: Vatandas Ihbar Portali

Ayri domain/subdomain:

- `ihbar.DOMAIN`

Route:

- `/`

Icerik:

- Harita uzerinden konum secimi
- Aciklama
- Fotograf yukleme
- Ihbari gonder
- Basari mesaji

Backend durumu:

- Public ihbar endpoint'i mevcut.
- Fotograf yukleme icin backend genisletmesi gerekecek.
- Harita koordinatlari ve adres alanlari netlestirilecek.

Tasarim:

- Personel panelinden daha sade
- Buyuk butonlar
- Mobil uyumlu
- Uyelik yok

## Faz 9: Yayinlama

1. Web build al.
2. Nginx ile paneli yayinla.
3. Vatandas portalini ayri domain/subdomain'e bagla.
4. API reverse proxy ayarla.
5. Backend'i systemd servisine tasiyarak kalici hale getir.
6. HTTPS icin domain geldikten sonra sertifika ekle.

## Ilk Uygulama Sirasi

1. Web iskelet
2. Login
3. Rol bazli layout
4. Admin filo sayfasi
5. Sofor gorev sayfasi
6. Bakim arac sayfasi
7. Personel backend endpoint'leri + personel sayfasi
8. Konteyner backend endpoint'leri + konteyner sayfasi
9. Muhasebe sayfalari
10. Operator sayfalari
11. Vatandas ihbar portali
