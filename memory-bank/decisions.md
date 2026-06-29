# Decisions

Bu dosya proje içinde netleşen kararların kısa kayıt tutarıdır.

## 2026-06-29 Kararları

- Proje ana hedefi web tabanlı MVP olarak belirlenmiştir. Backend ve frontend birlikte geliştirilir, web arayüz aktif üretim akışı olur.
- Backend API-first kalır; tüm ekranlar aynı API üzerinden çalışır.
- Rol bazlı erişim, görev havuzu ve audit log temel iş kurallarıdır.
- Vatandaş ihbarı doğrudan şoföre değil önce görev havuzuna düşer.
- Operasyonel kayıtların muhasebe akışına bağlanması zorunludur; bakım ve satış işlemleri bekleyen gider/gelir kaydı üretir.
- Harita, rota ve konum akışları web panelde canlı çalışır; gerçek IoT veya karmaşık rota optimizasyonu MVP kapsamında değildir.
- Desktop/legacy ekranlar artık ana geliştirme hedefi değildir; gerektiğinde ayrı bakım olarak ele alınır.
- Her değişiklikte test ve build doğrulaması yapılır; memory bank güncel tutulur.
- README, dokümantasyon ve memory bank aynı anda güncel tutulur; proje sunum ve teslim hazırlığı için bu belge seti tek kaynak olarak kullanılır.
