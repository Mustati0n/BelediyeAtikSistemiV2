# Active Context

## Güncel odak

Proje artık web-first MVP olarak canlı ve doğrulanmış durumda. Öncelik, mevcut backend ve web arayüzünü stabil tutmak, rol bazlı akışları korumak ve sunuma hazır kalmaktır.

## Mevcut sistem durumu

- Backend: FastAPI, SQLAlchemy 2.x, Alembic, PostgreSQL, JWT tabanlı auth, rol bazlı yetkilendirme ve audit log desteği.
- Web panel: React + TypeScript + Vite, Leaflet/OpenStreetMap ve OSRM tabanlı harita/rota akışları.
- Ana roller: admin, sürücü, bakım, muhasebe, geri dönüşüm operatörü ve vatandaş ihbar portalı.
- Canlı dağıtım: Nginx üzerinden web panel ve API erişimi mevcut; HTTPS desteği de aktif durumda.

## Son durumda tamamlanan geliştirmeler

- Auth, RBAC ve audit altyapısı kuruldu; demo kullanıcılar ve seed verileri hazırlandı.
- Vatandaş ihbarı, görev havuzu, görev atama ve sürücü görev akışı tamamlandı.
- Konteyner yönetimi, kritik seviye tetikleyici ve görev oluşturma akışı çalışır durumda.
- Bakım kayıtları, gider akışı, teknik tamamlama ve muhasebe onay akışı entegre edildi.
- Tesis teslimi, ayırıştırma, stok hareketi ve satış akışı işletilebilir hale getirildi.
- Muhasebe ekranı; bekleyen gelir/gider, bordro, maaş ve raporlama akışlarını kapsar.
- Admin denetim dashboard, personel, filo, konteyner, görevler, loglar, finans ve ayarlar ekranları canlı backend’e bağlanmıştır.
- Vatandaş portalı ihbar formu, fotoğraf yükleme, konum seçimi ve ihbar durumu sorgulama desteği ile çalışır durumda.
- Sürücü ekranı rota haritası, görev detayı, başlatma/sonuçlandırma ve optimize modu ile kullanılabilir hale geldi.
- Responsive UI iyileştirmeleri, harita tabanlı düzenlemeler ve bildirim/aksiyon akışları tüm ana ekranlara uygulanmıştır.

## Aktif kararlar

- Proje yapısı web-first MVP olarak korunacaktır; eski masaüstü odaklı çalışmaların önceliği yoktur.
- Yeni özellikler eklenmeden önce backend API, doğrulama kuralları ve UI akışı birlikte düşünülmelidir.
- Yetki ayrımı ve audit loglar ana kalite kriteri olarak korunacaktır.
- Demo verileri ve canlı ortam akışları, gelecekteki geliştirmeler için referans niteliğinde tutulacaktır.

## Dikkat edilmesi gereken noktalar

- Her yeni geliştirme, mevcut canlı sistemle uyumlu ve test edilmiş şekilde yapılmalıdır.
- Yeni ekran veya endpoint eklenirken hem backend testleri hem web build doğrulaması yapılmalıdır.
- Memory Bank, gerçek uygulama durumu ile senkron kalmalıdır.

## Sonraki adım

Mevcut sistemin sunuma, demo akışına ve manuel QA süreçlerine hazır tutulması önceliklidir. İleride eklenebilecek iyileştirmeler küçük ve odaklı olmalı, mevcut MVP yapısını bozacak değişikliklerden kaçınılmalıdır.
