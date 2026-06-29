# Sunum ve Manuel Test Plani

Bu plan, sistemi sunumdan once hizlica kontrol etmek ve demo sirasinda hangi
adimlarin gosterilecegini netlestirmek icin hazirlandi.

## 1. Sistem Saglik Kontrolu

| Kontrol | Beklenen |
| --- | --- |
| `http://77.83.37.48:8000/api/v1/health` | `{"status":"ok","service":"backend"}` |
| `http://77.83.37.48/admin` | Web panel acilir |
| `http://77.83.37.48/ihbar` | Vatandas ihbar portali acilir |
| `npm run build` | Basarili build |
| `.venv/bin/pytest` | Tum backend testleri gecer |

Son dogrulama: backend test paketi `41 passed`, web build basarili.

## 2. Demo Kullanici Girisleri

| Sira | Rol | Kullanici | Sifre | Beklenen |
| --- | --- | --- | --- | --- |
| 1 | Admin | `admin@belediye.local` | `Admin123!` | `/admin` |
| 2 | Sofor | `sofor@belediye.local` | `Sofor123!` | `/driver/gorevler` |
| 3 | Bakim | `bakim@belediye.local` | `Bakim123!` | `/maintenance/bakim` |
| 4 | Muhasebe | `muhasebe@belediye.local` | `Muhasebe123!` | `/finance/muhasebe` |
| 5 | Operator | `operator@belediye.local` | `Operator123!` | `/recycling/tesis` |

## 3. Ana Demo Senaryosu

### Adim 1: Vatandas Ihbari

Adres: `/ihbar`

- Hizli test konumlarindan bir kurum sec.
- Aciklama yaz.
- Istege bagli fotograf yukle.
- Ihbari gonder.
- Ihbar numarasini not al.

Beklenen:

- Basari mesaji gorunur.
- Ihbar numarasi ve gorev numarasi uretilir.
- Durum sorgulama ayni ihbari bulur.

### Adim 2: Admin Gorev Havuzu

Adres: `/admin/gorevler`

- Yeni ihbari gorev havuzunda bul.
- Sofor ve aktif arac sec.
- `Sira Oner` kullan.
- Gorevi ata.

Beklenen:

- Gorev `Atandi` durumuna gecer.
- Admin log kaydinda gorev atama gorunur.

### Adim 3: Sofor Rota ve Gorev

Adres: `/driver/gorevler`

- Atanmis gorev haritada pin olarak gorunur.
- OSRM yol rotasi veya yedek rota cizilir.
- Gorevi baslat.
- Gorev sonuc modalindan `Tamamlandi` sec.

Beklenen:

- Gorev durumu `Islemde`, sonra `Tamamlandi` olur.
- Admin dashboard/gorev ekraninda sayilar guncellenir.

### Adim 4: Bakim Akisi

Adres: `/maintenance/bakim`

- Yeni bakim kaydi ac.
- Bakim turu, oncelik, parca/iscilik maliyeti gir.
- Teknik tamamlama yap.

Beklenen:

- Arac bakim surecine girer.
- Muhasebeye bekleyen gider kaydi duser.
- Teknik tamamlama ile arac operasyonel hale gelir.

### Adim 5: Geri Donusum Tesisi

Adres: `/recycling/tesis`

- Bekleyen teslimi onayla.
- Teslimi atik turlerine ayristir.
- Stoktan satis olustur.

Beklenen:

- Stok artar.
- Satis stoktan duser.
- Muhasebeye bekleyen gelir kaydi duser.

### Adim 6: Muhasebe

Adres: `/finance/muhasebe`

- Bekleyen gelir/gider kayitlarini incele.
- Bir gelir veya gideri onayla.
- Personel kartindan ek kalemli maas hesapla.

Beklenen:

- Kar-zarar ozeti guncellenir.
- Onaylanan kayit kuyruktan cikar.
- Bordro odeme aciklamasinda ek kalem ozeti gorunur.

### Adim 7: Admin Log ve Denetim

Adresler: `/admin`, `/admin/loglar`

- Son loglari kontrol et.
- Islem tipi veya kullanici filtresi uygula.
- Sayfalama ve CSV aktarim butonlarini kontrol et.

Beklenen:

- Demo boyunca yapilan islemler audit log olarak gorunur.
- Dashboard operasyon durumunu ozetler.

## 4. Responsive Kontrol

| Genislik | Kontrol |
| --- | --- |
| 1440px | Admin dashboard ve tablolar dengeli gorunmeli |
| 1366px | Sidebar ve dashboard panelleri sikismamali |
| 1180px | Gridler iki kolon/tek kolon kirilimina gecmeli |
| 760px | Formlar tek kolon, butonlar tam genislik olmali |
| Mobil | Harita ve modal ekranlari kaydirilarak kullanilabilmeli |

## 5. Sunumda Vurgulanacak Ozellikler

- Rol bazli giris ve yetki ayrimi.
- Vatandas ihbarinin otomatik gorev havuzuna dusmesi.
- Adminin haritadan gorev olusturabilmesi.
- Konteyner doluluk simulasyonu ve kritik gorev uretimi.
- Sofor icin gercek yol rotasi.
- Bakimdan muhasebeye otomatik gider akisi.
- Geri donusum stok ve satis akisi.
- Muhasebe onaylari ve personel bordro karti.
- Admin audit log ve sistem parametreleri.

## 6. Kalan Son Kontroller

- Gercek cihazlarda goz testi.
- Sunum sirasinda kullanilacak demo verisinin temizlenmesi veya seed ile yenilenmesi.
- Ekran goruntulerinin hazirlanmasi.
- API endpoint listesinin rapora eklenmesi.
