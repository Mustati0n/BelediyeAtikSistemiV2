from services.api_client import api_client


class DriverService:
    _shift_status = "Hazır"
    _delivery_history = []

    @staticmethod
    def _task_type_label(task_type):
        return {
            "Ihbar": "Vatandaş İhbarı",
            "KritikKonteyner": "Kritik Konteyner",
        }.get(task_type, task_type)

    @staticmethod
    def _status_label(status):
        return {
            "Atandi": "Atandı",
            "Islemde": "İşlemde",
            "Tamamlandi": "Tamamlandı",
            "Basarisiz": "Başarısız",
        }.get(status, status)

    @staticmethod
    def _priority_label(priority):
        if priority >= 9:
            return "Yüksek"
        if priority >= 5:
            return "Orta"
        return "Düşük"

    @staticmethod
    def _build_title(task):
        if task["tip"] == "Ihbar":
            return "Vatandaş İhbarı"
        if task["kaynak"]["tip"] == "Konteyner":
            return "Kritik Konteyner Doluluğu"
        return DriverService._task_type_label(task["tip"])

    @classmethod
    def _vehicle_from_task(cls, task):
        vehicle = task.get("kullanilan_arac")
        if vehicle is None:
            return {
                "vehicle_name": "Araç ataması bekleniyor",
                "plate": "-",
                "capacity_kg": 0,
                "vehicle_type": "-",
                "region": "-",
                "status": "Atanmadı",
            }
        return {
            "vehicle_name": "Atanmış Araç",
            "plate": vehicle["plaka"],
            "capacity_kg": vehicle["kapasite_kg"],
            "vehicle_type": vehicle["tip"],
            "region": "-",
            "status": vehicle["durum"],
        }

    @classmethod
    def _normalize_task(cls, task):
        source = task["kaynak"]
        location = (
            f"Konteyner #{source['id']}"
            if source["tip"] == "Konteyner"
            else f"İhbar #{source['id']}"
        )
        return {
            "id": task["id"],
            "title": cls._build_title(task),
            "task_type": cls._task_type_label(task["tip"]),
            "priority": cls._priority_label(task["oncelik"]),
            "status": cls._status_label(task["durum"]),
            "location": location,
            "description": task.get("aciklama") or source["aciklama"],
            "lat": str(source["enlem"]),
            "lng": str(source["boylam"]),
            "vehicle": cls._vehicle_from_task(task),
        }

    @staticmethod
    def _result_to_api(result_type):
        mapping = {
            "Ulaşılamadı": "Ulasilamadi",
            "Yanlış İhbar": "YanlisIhbar",
            "Tekrar Kontrol Gerekli": "TekrarKontrolGerekli",
        }
        return mapping[result_type]

    def get_shift_info(self):
        current_user = api_client.current_user or {}
        tasks = self.get_tasks()
        assigned_vehicle = tasks[0]["vehicle"] if tasks else self._vehicle_from_task({})
        return {
            "driver_name": current_user.get("ad_soyad", "Şoför"),
            "shift_status": self._shift_status,
            "assigned_vehicle": assigned_vehicle,
        }

    def start_shift(self):
        self.__class__._shift_status = "Vardiya Başladı"
        return self.get_shift_info()

    def get_daily_route_summary(self):
        tasks = self.get_tasks()
        return {
            "task_count": len(tasks),
            "priority_tasks": len([task for task in tasks if task["priority"] == "Yüksek"]),
            "region": tasks[0]["vehicle"]["region"] if tasks else "-",
        }

    def get_tasks(self):
        payload = api_client.get("/operations/sofor/gorevler/gunluk")
        return [self._normalize_task(task) for task in payload.get("gorevler", [])]

    def get_task_by_id(self, task_id):
        for task in self.get_tasks():
            if task["id"] == task_id:
                return task
        return None

    def start_task(self, task_id):
        api_client.post(f"/operations/gorevler/{task_id}/baslat")
        return self.get_task_by_id(task_id)

    def complete_task(self, task_id):
        api_client.post(
            f"/operations/gorevler/{task_id}/sonuclandir",
            {"sonuc": "Tamamlandi", "aciklama": "Görev tamamlandı."},
        )
        return self.get_task_by_id(task_id)

    def fail_task(self, task_id, result_type, note=""):
        api_client.post(
            f"/operations/gorevler/{task_id}/sonuclandir",
            {"sonuc": self._result_to_api(result_type), "aciklama": note or result_type},
        )
        return self.get_task_by_id(task_id)

    def get_delivery_history(self):
        return [delivery.copy() for delivery in self._delivery_history]

    def submit_delivery(self, total_kg, note):
        payload = api_client.post(
            "/recycling/teslimler",
            {"toplam_kg": float(total_kg), "aciklama": note or None},
        )
        delivery = {
            "id": payload["id"],
            "date": payload["tarih"],
            "total_kg": float(payload["toplam_kg"]),
            "note": payload.get("aciklama") or "",
        }
        self.__class__._delivery_history.insert(0, delivery)
        return delivery.copy()

    def close_shift(self):
        self.__class__._shift_status = "Vardiya Kapatıldı"
        return self.get_shift_info()
