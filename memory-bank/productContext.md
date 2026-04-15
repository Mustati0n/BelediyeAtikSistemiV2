# Product Context

## Neden Var?

Belediye atik operasyonlari cok sayida bolunmus is akisindan olusur: vatandas ihbarlari, konteyner takibi, saha gorevleri, arac bakimi, tesis stoklari ve muhasebe surecleri genelde ayri takip edilir. Bu proje bu operasyonlari tek sistemde birlestirerek gorevlerin, maliyetlerin ve durumlarin izlenebilir olmasini hedefler.

## Cozulen Problemler

- Ihbarlarin kaybolmasi veya dogrudan sahaya plansiz dusmesi.
- Kritik dolu konteynerlerin manuel takip edilmesi.
- Arac bakim maliyetlerinin finans surecine kontrolsuz aktarilmasi.
- Geri donusum satis gelirlerinin operasyonla kopuk izlenmesi.
- Personel maas, avans ve toplu odeme islemlerinde tekrar ve hata riski.
- Sistem yoneticisinin operasyonel ve finansal tabloyu tek yerden goremeyisi.

## Beklenen Deneyim

- Yonetici icin yogun ama taranabilir dashboard, tablolar, filtreler ve grafikler.
- Sofor icin sade, gorev odakli ve harita destekli operasyon ekrani.
- Bakim teknisyeni icin arac secimi ve bakim kaydi girisini hizli yapan formlar.
- Muhasebe icin bekleyen gider/gelir onaylari, maas islemleri ve raporlarin ayrildigi net ekranlar.
- Geri donusum operatoru icin teslim alma, ayristirma, stok ve satis akisinin sirali ilerledigi ekranlar.
- Vatandas icin uyeliksiz, acik ve kolay ihbar formu.

## Urun Ilkeleri

- Rol bazli yetkilendirme temel kuraldir.
- Ana operasyon birimi `Gorev` kaydidir.
- Durum alanlari sureclerin omurgasidir.
- Operasyonel kayit finansal kayda otomatik ama onay bekleyen sekilde donusur.
- MVP'de sensor ve rota optimizasyonu gercek entegrasyon yerine simulasyon ve basit siralama ile ilerler.
