# Project Brief

## Proje

Akilli Sehir Atik Yonetimi ve Geri Donusum Sistemi, belediyeye bagli atik toplama, vatandas ihbari, konteyner doluluk takibi, arac bakimi, geri donusum tesisi ve finans operasyonlarini tek merkezden yonetmek icin gelistirilecek entegre bir yazilim sistemidir.

Ana kaynak rapor:

- `/home/mustati0n/İndirilenler/TasarimRaporu/Akıllı Şehir Atık Yönetimi ve Geri Dönüşüm Sistemi 31fae0a42aa680c4b45bff3b0a6164bd.md`

## Kapsam

Sistem asagidaki modulleri kapsar:

- Sistem yoneticisi modulu: personel, rol, sistem parametreleri, bolge, konteyner, arac, dashboard ve audit log yonetimi.
- Vatandas ihbar portali: uyeliksiz web ihbar formu, konum, aciklama ve fotograf yukleme.
- Akilli konteyner ve IoT simulasyonu: sensor yerine arka plan servisinin konteyner doluluklarini uretmesi.
- Gorev havuzu ve rota: vatandas ihbarlari ile kritik konteynerlerin sofore dogrudan degil, gorev havuzuna dusmesi.
- Sofor operasyonu: gunluk rota, gorev baslatma, gorev sonuclandirma, tesise atik teslimi.
- Bakim yonetimi: arac bakim/ariza kaydi, arac durumunun bakimda isaretlenmesi, gider kaydi uretimi.
- Muhasebe ve finans: maas, avans/tekli/toplu odeme, bekleyen gider/gelir onayi, kar/zarar raporu.
- Geri donusum tesisi: teslim alma, ayristirma, stok hareketi, satis, gelir onay sureci.

## Kapsam Disi

- Gercek fiziksel IoT sensor entegrasyonu.
- Canli GPS arac takibi.
- Harici banka veya odeme sistemi entegrasyonu.
- Mobil uygulama.
- Yapay zeka tabanli fotograf dogrulama.
- Cok kurumlu veya cok belediyeli yapi.
- Gercek zamanli trafik verisiyle ileri rota optimizasyonu.
- Vatandas icin uyelikli tam takip sistemi.

## Kullanici Rolleri

- Vatandas
- Sistem Yoneticisi
- Muhasebe Personeli
- Bakim Teknisyeni
- Sofor
- Geri Donusum Operatoru

## Basari Kriterleri

- Her rol yalnizca kendi ekranlarina ve islemlerine erisir.
- Ihbarlar ve kritik konteynerler merkezi gorev havuzunda toplanir.
- Acik gorev varken ayni konteyner icin tekrar eden gorev olusmaz.
- Bakim kayitlari muhasebeye bekleyen gider olarak akar.
- Satis kayitlari muhasebeye bekleyen gelir olarak akar.
- Toplu maas odemesi yalnizca ayin 15'inde calisir.
- Kritik islemler audit log'a yazilir.
- Sistem MVP asamasinda Linux ortaminda calisabilir ve test edilebilir olur.
