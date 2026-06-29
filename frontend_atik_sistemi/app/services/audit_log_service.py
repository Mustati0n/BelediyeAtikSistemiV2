class AuditLogService:
    def __init__(self):
        self._logs = [
            {
                "id": 1,
                "date": "15.04.2026 09:18",
                "user": "Selin Aksoy",
                "action_type": "Kullanici Guncelleme",
                "description": "Emre Kaya personel kaydi guncellendi.",
                "entity_type": "Personel",
                "entity_id": 12,
            },
            {
                "id": 2,
                "date": "15.04.2026 10:42",
                "user": "Merve Tas",
                "action_type": "Sistem Parametresi Degisikligi",
                "description": "Kritik konteyner doluluk esigi %80 -> %85 olarak guncellendi.",
                "entity_type": "Sistem Parametresi",
                "entity_id": 3,
            },
            {
                "id": 3,
                "date": "15.04.2026 11:05",
                "user": "Ahmet Yilmaz",
                "action_type": "Arac Durumu Guncelleme",
                "description": "34 ABC 123 plakali arac bakimda olarak isaretlendi.",
                "entity_type": "Arac",
                "entity_id": 4,
            },
            {
                "id": 4,
                "date": "15.04.2026 11:48",
                "user": "Elif Demir",
                "action_type": "Gelir Onayi",
                "description": "Satis kaydi muhasebe tarafindan onaylandi.",
                "entity_type": "Gelir Kaydi",
                "entity_id": 27,
            },
            {
                "id": 5,
                "date": "15.04.2026 13:20",
                "user": "Murat Acar",
                "action_type": "Bakim Kaydi Olusturma",
                "description": "06 XYZ 990 araci icin yeni bakim kaydi acildi.",
                "entity_type": "Bakim Kaydi",
                "entity_id": 19,
            },
        ]

    def get_all(self):
        return [log.copy() for log in self._logs]
