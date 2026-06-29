# Belediye Atik Sistemi Kullanim Kilavuzu

Bu dokuman okul projesi demo ortami icindir. Sistem tek sunucu IP adresi
uzerinden personel paneli, vatandas ihbar portali ve backend API olarak calisir.

## Canli Adresler

- Personel paneli: `http://77.83.37.48`
- Vatandas ihbar ekrani: `http://77.83.37.48/ihbar`
- Alternatif ihbar adresi: `http://77.83.37.48/vatandas`
- Backend API: `http://77.83.37.48:8000/api/v1`
- Backend health: `http://77.83.37.48:8000/api/v1/health`
- HTTPS deneme: `https://77.83.37.48`

Not: HTTPS IP uzerinden self-signed sertifika ile calisir. Tarayici ilk giriste
sertifika uyarisi gosterebilir. Vatandas konum izni icin HTTPS adresi tercih
edilebilir.

## Demo Kullanici Bilgileri

| Rol | E-posta | Sifre | Giris sonrasi ekran |
| --- | --- | --- | --- |
| Sistem Yoneticisi | `admin@belediye.local` | `Admin123!` | `/admin` |
| Sofor | `sofor@belediye.local` | `Sofor123!` | `/driver/gorevler` |
| Bakim Teknisyeni | `bakim@belediye.local` | `Bakim123!` | `/maintenance/bakim` |
| Muhasebe Personeli | `muhasebe@belediye.local` | `Muhasebe123!` | `/finance/muhasebe` |
| Geri Donusum Operatoru | `operator@belediye.local` | `Operator123!` | `/recycling/tesis` |

## Rol Bazli Ekranlar

### Admin

- `/admin`: denetim merkezi, operasyon haritasi, KPI, finans ozeti ve son loglar.
- `/admin/filo`: arac listeleme, ekleme ve durum guncelleme.
- `/admin/personel`: personel listeleme, ekleme, rol ve aktiflik yonetimi.
- `/admin/konteynerler`: bolge/konteyner yonetimi, harita, doluluk ve simulasyon.
- `/admin/gorevler`: gorev havuzu, haritadan gorev olusturma, sofor/arac atama.
- `/admin/finans`: admin icin finans denetim ozeti.
- `/admin/parametreler`: sistem esikleri ve birim fiyat parametreleri.
- `/admin/loglar`: audit log arama, filtreleme, sayfalama ve CSV aktarim.

Admin, diger rollerin operasyon ekranlarini izleme amacli gorebilir; operasyonel
aksiyonlar ilgili role aittir.

### Sofor

- `/driver/gorevler`: gunluk gorevler, Gaziantep haritasi, OSRM yol rotasi,
  rota optimize/manual modu, gorev baslatma ve sonuclandirma.

### Bakim

- `/maintenance/bakim`: bakim kokpiti, is emri, arac bakim kaydi, parca/iscilik
  maliyeti, teknik tamamlama, gecmis ve CSV aktarim.

### Muhasebe

- `/finance/muhasebe`: finans kokpiti, gelir/gider onaylari, kar-zarar ozeti,
  bordro, personel karti, mesai/prim/kesinti ek kalemleri.

### Geri Donusum Tesisi

- `/recycling/tesis`: tesis teslimleri, teslim onayi, ayristirma, stoklar,
  stoktan satis, satis/stok hareket gecmisi ve CSV aktarim.

### Vatandas

- `/ihbar` veya `/vatandas`: uyeliksiz ihbar formu. Aciklama, haritadan konum,
  hizli test konumu, tarayici konumu ve opsiyonel fotograf yukleme desteklenir.
  Kayit tamamlaninca ihbar otomatik gorev havuzuna duser. Ihbar numarasi ile
  durum sorgulanabilir.

## Onerilen Demo Akisi

1. Vatandas portalindan bir ihbar olustur.
2. Admin ile giris yap ve `/admin/gorevler` ekraninda ihbari gorev havuzunda bul.
3. Admin, gorevi demo sofore ve aktif araca ata; gerekirse `Sira Oner` kullan.
4. Sofor ile giris yap, `/driver/gorevler` ekraninda rotayi gor.
5. Sofor gorevi baslatir ve sonuc modalindan tamamlar.
6. Geri donusum operatoru `/recycling/tesis` ekraninda bekleyen teslimi onaylar,
   ayrisir ve stoktan satis olusturur.
7. Muhasebe `/finance/muhasebe` ekraninda gelir/gider kayitlarini inceler ve onaylar.
8. Admin `/admin` ve `/admin/loglar` ekranlarinda son durum ve loglari kontrol eder.

## Manuel Test Listesi

### Genel

- Login ekraninda backend baglanti durumu hazir gorunuyor mu?
- Her rol giris sonrasi dogru ekrana gidiyor mu?
- Yetkisiz URL elle yazildiginda kullanici kendi ana ekranina donuyor mu?
- Cikis butonu session'i temizliyor mu?
- HTTP ve HTTPS ana route'lari aciliyor mu?

### Admin

- Dashboard KPI kartlari ve operasyon haritasi dolu geliyor mu?
- Filo ekraninda arac ekleme/durum guncelleme calisiyor mu?
- Personel ekraninda yeni kullanici ekleme ve aktif/pasif guncelleme calisiyor mu?
- Konteyner ekraninda harita pinleri, doluluk guncelleme ve simulasyon calisiyor mu?
- Gorevler ekraninda haritadan nokta secip gorev olusturma calisiyor mu?
- Gorev atama sofor/arac/sira bilgisiyle calisiyor mu?
- Log ekraninda arama, filtre ve sayfalama calisiyor mu?
- Parametre ekraninda degisiklik kaydedilebiliyor mu?

### Sofor

- Gorev listesi atanmis gorevleri gosteriyor mu?
- Harita Gaziantep merkezli aciliyor mu?
- OSRM yol rotasi veya yedek rota gorunuyor mu?
- Gorev baslatma ve sonuclandirma calisiyor mu?
- Tamamlanan gorev admin ekraninda guncelleniyor mu?

### Bakim

- Arac secerek bakim kaydi acilabiliyor mu?
- Bakim kaydi acilinca arac `Bakimda` durumuna geciyor mu?
- Parca/iscilik maliyeti toplam gideri etkiliyor mu?
- Teknik tamamlama araci tekrar aktif hale getiriyor mu?
- Muhasebede bekleyen gider olusuyor mu?

### Muhasebe

- Bekleyen gider ve gelir listeleri geliyor mu?
- Onay/red aksiyonlari calisiyor mu?
- Kar-zarar ozeti guncelleniyor mu?
- Personel kartinda maas hesaplama ve ek kalemler calisiyor mu?
- Tekli/avans odeme aciklamasi kayda isleniyor mu?

### Geri Donusum Operatoru

- Bekleyen teslimler listeleniyor mu?
- Teslim onayi calisiyor mu?
- Ayristirma stok hareketi olusturuyor mu?
- Stoktan satis stok miktarini dusuruyor mu?
- Satis bekleyen gelir olarak muhasebeye dusuyor mu?

### Vatandas

- Haritadan nokta secimi forma enlem/boylam yaziyor mu?
- Hizli test konumlari acilir panelden secilebiliyor mu?
- Fotograf yukleme ve onizleme calisiyor mu?
- Ihbar kaydi gorev havuzuna dusuyor mu?
- Ihbar durum sorgulama calisiyor mu?

### Responsive

- 1366px laptop genisliginde paneller tasma yapmiyor mu?
- 1180px civarinda dashboard gridleri okunur kaliyor mu?
- 760px altinda formlar tek kolona dusuyor mu?
- Mobilde islem butonlari tam genislik ve okunur mu?
- Harita panelleri dikey kaydirma ile kullanilabilir mi?
