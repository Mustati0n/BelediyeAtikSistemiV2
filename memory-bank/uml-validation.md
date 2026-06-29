# UML Validation Notes

Kaynaklar:

- Use-case gorseli: `image.png`
- Eski domain modeli: `image 1.png`
- Yeni domain modeli: `image 2.png`
- Bakim/gider/muhasebe sequence: `image 3.png`
- Ihbar/IoT/rota sequence: `image 4.png`
- Tesis/stok/satis/gelir sequence: `image 5.png`

## Use-Case Diyagrami

Durum: Genel olarak kapsamla uyumlu.

Dogru gorunenler:

- Vatandas sadece `Cevre Ihbari Olustur` ile sinirli.
- Personel rolleri login uzerinden kendi ekranlarina ayriliyor.
- Sistem yoneticisi merkezi yonetim ve log inceleme yetkilerine sahip.
- Muhasebe; maas, gider, gelir ve kar/zarar alanlarini kapsiyor.
- Sofor; rota, gorev sonucu ve tesis teslim akisini kapsiyor.
- Operator; teslim alma, ayristirma, stok ve satis akisini kapsiyor.

Duzeltme/Netlestirme notlari:

- `Sisteme Giris Yap` tum personel rollerinde ortak use-case; diyagramda baglanti var, uygulamada ortak auth modulu olmali.
- Vatandas uyeliksiz oldugu icin login kullanmayacak.
- Admin icin `Bakim Giderleri` veya `Gelir Onaylari` dogrudan islev degil, dashboard sayaclari olarak gorulebilir.

## Domain Modeli

Durum: Yeni yapi uygulanacak ana model olarak alinmali.

Dogru kararlar:

- Eski kalitimli personel modeli yerine `Personel` + `Rol` daha sade ve veritabani dostu.
- `Gorev` merkezi operasyon kaydi olarak dogru konumda.
- `BakimKaydi -> GiderKaydi` ve `Satis -> GelirKaydi` finansal onay akisini destekliyor.
- `Stok`, `StokHareketi`, `Satis` tesis sureci icin yeterli MVP cekirdegi veriyor.

Uygulama oncesi eklenmesi gerekenler:

- `Konteyner` modelinde `bolge_id` foreign key acikca olmalı.
- `Gorev` modelinde `ihbar_id` ve `konteyner_id` nullable foreign key olarak olmalı; is kurali olarak tam biri dolu olmali.
- `Gorev.Sonuc` ve `Gorev.TamamlanmaTarihi` baslangicta nullable olmali.
- `Ihbar.FotografUrl` nullable veya optional olmali; vatandas fotograf yuklemeyebilir mi karar verilecek.
- `TesisTeslim` icin `teslim_eden_sofor_id` ve `teslim_alan_operator_id` ayrimi daha temiz olur.
- Sistem parametreleri raporda var ama domain diyagraminda yok; `SistemParametresi` tablosu eklenmeli.
- Maas tekrarini engellemek icin `MaasOdeme` uzerinde personel + donem + odeme tipi kurali tasarlanmali.
- Ayni konteyner icin acik gorev tekrarini engelleyen indeks veya servis kontrolu gerekir.

## Bakim / Gider / Muhasebe Sequence

Durum: Ana finansal akis dogru, bir is kurali tartismali.

Dogru akis:

- Bakim teknisyeni bakim kaydi aciyor.
- Arac durumu `Bakimda` oluyor.
- Bekleyen `GiderKaydi` olusuyor.
- Muhasebe bekleyen gideri onayliyor veya reddediyor.

Karar:

- Bakim olustugunda bekleyen `GiderKaydi` muhasebeye hemen dusecek.
- Fiziksel bakim tamamlanmasi ile muhasebe gider onayi ayrik tutulacak.
- Muhasebe gideri onayladiginda mali kayit kesinlesir; aracin tekrar `Aktif` olmasi teknik bakim tamamlanma aksiyonuna baglanir.

## Ihbar / IoT / Rota Sequence

Durum: Uygulama icin guclu ve tutarli.

Dogru akis:

- Vatandas ihbari `Bekliyor` durumunda olusuyor.
- Ihbar icin `Gorev` olusuyor.
- IoT simulasyonu konteyner doluluklarini guncelliyor.
- Kritik esik asilirsa acik gorev kontrolu yapiliyor.
- Sofor gunluk gorevleri aliyor, baslatiyor, sonuclandiriyor.

Netlestirme gereken nokta:

- Gorev basarisiz ise kaynak ihbar/konteyner durumunun ne olacagi sonuc tipine gore belirlenmeli.
- `YanlisIhbar` sonucunda ihbar `Gecersiz` olabilir.
- `TekrarKontrolGerekli` sonucunda yeni bekleyen gorev veya ayni gorevin tekrar planlanmasi gerekebilir.

## Tesis / Stok / Satis / Gelir Sequence

Durum: Gorsel var, fakat markdown raporda PlantUML kodu gorunmuyor.

Gorselden cikan akis:

- Sofor tesis teslim kaydi olusturur.
- Operator teslimi gorur ve onaylar.
- Operator atigi turlerine gore ayristirir.
- Stok hareketleri olusur ve stok artar.
- Operator stoktan satis kaydi olusturur.
- Satis bekleyen gelir kaydi uretir.
- Muhasebe gelir kaydini onaylar veya reddeder.

Uygulama oncesi yapilacak:

- Bu sequence icin PlantUML kodu yeniden yazilmali.
- MVP karari: satis dogrudan yapilacak, stok satis aninda duser. Stok rezervasyon ve red halinde geri ekleme detayi simdilik yok.
- Teslim kaydinin onaylanmadan ayristirilip ayristirilamayacagi belirlenmeli.
