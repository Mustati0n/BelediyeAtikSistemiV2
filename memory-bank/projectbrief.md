# Project Brief

## Proje

Akıllı Şehir Atık Yönetimi ve Geri Dönüşüm Sistemi, belediyeye bağlı atık toplama, vatandaş ihbarı, konteyner doluluk takibi, araç bakımı, geri dönüşüm tesisi ve finans operasyonlarını tek merkezden yönetmek için geliştirilen web tabanlı bir MVP platformudur.

Bu sürüm, canlı çalışan bir web paneli, FastAPI tabanlı backend ve rol bazlı iş akışları ile sunuma hazır duruma getirilmiştir.

## Ana Amaç

- Vatandaş ihbarlarını merkezi görev havuzuna almak.
- Kritik konteyner olaylarını operasyonel görev haline getirmek.
- Şoför, bakım, muhasebe ve tesis operasyonlarını ortak bir API ve rol bazlı arayüz üzerinden yürütmek.
- Operasyonel kayıtların muhasebe ve audit akışına bağlanmasını sağlamak.

## Kapsam

Sistem şu modülleri kapsar:

- Yönetim ve denetim: personel, rol, sistem parametreleri, bölge, konteyner, araç, dashboard ve audit log yönetimi.
- Vatandaş ihbar portalı: üyeliksiz web ihbar formu, konum, açıklama ve fotoğraf yükleme.
- Görev havuzu ve rota: vatandaş ihbarları ve kritik konteyner olayları doğrudan şoföre değil, merkezi görev havuzuna düşer.
- Şoför operasyonu: günlük rota, görev başlatma, görev sonuçlandırma, tesise atık teslimi.
- Bakım yönetimi: araç bakım/ariza kaydı, bakım durumu, gider kaydı üretimi.
- Muhasebe ve finans: maaş, avans/tekli/toplu ödeme, bekleyen gider/gelir onayı, kar/zarar raporu.
- Geri dönüşüm tesisi: teslim alma, ayırıştırma, stok hareketi, satış, gelir onay süreci.

## Kapsam Dışı

- Gerçek fiziksel IoT sensör entegrasyonu.
- Canlı GPS araç takibi.
- Harici banka veya ödeme sistemi entegrasyonu.
- Mobil uygulama.
- Yapay zeka tabanlı fotoğraf doğrulama.
- Çok kurumlu veya çok belediyeli yapı.
- Gerçek zamanlı trafik verisiyle ileri rota optimizasyonu.
- Vatandaş için üyelikli tam takip sistemi.

## Kullanıcı Rolleri

- Vatandaş
- Sistem Yöneticisi
- Muhasebe Personeli
- Bakım Teknisyeni
- Şoför
- Geri Dönüşüm Operatörü

## Başarı Kriterleri

- Her rol yalnızca kendi ekranlarına ve işlemlerine erişir.
- İhbarlar ve kritik konteynerler merkezi görev havuzunda toplanır.
- Açık görev varken aynı konteyner için tekrar eden görev oluşmaz.
- Bakım kayıtları muhasebeye bekleyen gider olarak akar.
- Satış kayıtları muhasebeye bekleyen gelir olarak akar.
- Toplu maaş ödemesi yalnızca ayın 15'inde çalışır.
- Kritik işlemler audit log'a yazılır.
- Sistem Linux ortamında çalışır, web paneli üretim build ile servis edilir ve backend testleri geçer.
