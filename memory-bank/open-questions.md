# Open Questions

Bu sorular cevaplaninca uygulama fazina daha hizli ve daha az geri donusle gecebiliriz. Cevap gelmezse yanlarindaki onerilen varsayimlarla ilerlenebilir.

## 1. Kod tabani nasil baslasin?

Durum: Cevaplandi.

Karar: Once backend/API ve veritabani, sonra vatandas portali ve PySide6 masaustu ekranlari.

Sebep: Domain modeli ve API oturmadan masaustu ekranlarinda cok revizyon cikar.

Ek karar: Frontend sonradan eklenecegi icin backend API-first kurulacak ve markdown raporundaki UI ekran ihtiyaclarina uygun endpoint/schema yapisi hazirlanacak.

## 2. PostgreSQL yerel mi, Docker Compose mu?

Durum: Cevaplandi.

Karar: Docker Compose.

Sebep: Demo, test ve kurulum tekrarlanabilir olur.

## 3. Bakim tamamlanmasi ile muhasebe gider onayi ayni olay mi?

Durum: Cevaplandi.

Karar: Ayrik olsun.

Sebep: Bakim teknisyeni fiziksel bakimi tamamlar; muhasebe sadece maliyeti onaylar. Aracin tekrar `Aktif` olmasi teknik tamamlanmaya baglanir.

Not: Bakim olustugunda muhasebeye bekleyen gider yine hemen dusecek. Ayrim sadece "bakim bitti" ile "muhasebe maliyeti onayladi" olaylarini karistirmamak icindir.

## 4. Satis reddedilirse stok ne olacak?

Durum: Cevaplandi.

Karar: MVP'de satis dogrudan yapilacak. Stok satis aninda duser, gelir kaydi muhasebe raporlama/onay akisi icin olusur. Stok rezervasyon ve reddedilince geri ekleme detayi simdilik yok.

Sebep: Ilk surumde satis akisini basit ve calisir tutmak daha oncelikli.

## 5. Vatandas fotograf yuklemek zorunda mi?

Durum: Cevaplandi.

Karar: Opsiyonel.

Sebep: Ihbar bariyerini dusurur; test ve MVP akisini kolaylastirir.

## 6. Sofor ekraninda harita MVP'de nasil olsun?

Durum: Cevaplandi.

Karar: PySide6 tarafinda ilk MVP'de gorev listesi + koordinat yeterli. Harita entegrasyonu is akisina sonraki UI iterasyonu olarak eklendi.

Sebep: PySide6 harita entegrasyonu zaman alabilir; operasyon akisini once calistirmak daha saglam.

## 7. Proje git deposu olarak baslatilsin mi?

Durum: Cevaplandi.

Karar: Evet, `git init` ile baslatilsin.

Sebep: Faz faz ilerlerken degisiklikleri guvenli takip ederiz.

Not: Commit mesajlarini Codex yazabilir. Push icin uzak GitHub/GitLab deposu ve yetki gerekir; uzak repo tanimlanana kadar commit'ler yerel kalir.
