from services.api_client import api_client


class VehicleService:
    @staticmethod
    def _normalize_vehicle(vehicle):
        return {
            "id": vehicle["id"],
            "plate": vehicle["plaka"],
            "type": vehicle["tip"],
            "capacity_kg": vehicle["kapasite_kg"],
            "status": vehicle["durum"],
            "region": vehicle.get("region") or "-",
            "last_maintenance": vehicle.get("last_maintenance") or "-",
        }

    @staticmethod
    def _status_to_api(status_text):
        mapping = {
            "Aktif": "Aktif",
            "Bakımda": "Bakimda",
            "Bakimda": "Bakimda",
            "Pasif": "Pasif",
        }
        return mapping.get(status_text, status_text)

    def get_all(self):
        payload = api_client.get("/fleet/araclar")
        return [self._normalize_vehicle(vehicle) for vehicle in payload.get("araclar", [])]

    def add_vehicle(self, vehicle_data):
        payload = {
            "plaka": vehicle_data["plate"],
            "tip": vehicle_data["type"],
            "kapasite_kg": int(vehicle_data["capacity_kg"]),
        }
        created = api_client.post("/fleet/araclar", payload)
        return self._normalize_vehicle(created)

    def update_vehicle(self, vehicle_id, updated_data):
        payload = {
            "tip": updated_data["type"],
            "kapasite_kg": int(updated_data["capacity_kg"]),
            "durum": self._status_to_api(updated_data["status"]),
        }
        updated = api_client.patch(f"/fleet/araclar/{vehicle_id}", payload)
        return self._normalize_vehicle(updated)

    def cycle_status(self, vehicle_id):
        vehicles = {vehicle["id"]: vehicle for vehicle in self.get_all()}
        vehicle = vehicles.get(vehicle_id)
        if vehicle is None:
            return None

        order = ["Aktif", "Bakımda", "Pasif"]
        current = vehicle["status"]
        current_index = order.index(current) if current in order else 0
        next_status = order[(current_index + 1) % len(order)]
        return self.update_vehicle(
            vehicle_id,
            {
                "type": vehicle["type"],
                "capacity_kg": vehicle["capacity_kg"],
                "status": next_status,
            },
        )
