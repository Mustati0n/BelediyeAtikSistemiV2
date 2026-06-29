from services.api_client import api_client


class MaintenanceService:
    @staticmethod
    def _normalize_vehicle(vehicle):
        return {
            "id": vehicle["id"],
            "plate": vehicle["plaka"],
            "type": vehicle["tip"],
            "status": vehicle["durum"],
            "capacity_kg": vehicle["kapasite_kg"],
            "last_maintenance": vehicle.get("last_maintenance") or "-",
        }

    def get_all_vehicles(self):
        payload = api_client.get("/fleet/araclar")
        return [self._normalize_vehicle(vehicle) for vehicle in payload.get("araclar", [])]
