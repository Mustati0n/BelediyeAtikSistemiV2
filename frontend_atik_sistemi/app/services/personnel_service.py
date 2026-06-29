class PersonnelService:
    def __init__(self):
        self._personnel = [
            {
                "id": 1,
                "name": "Emre Kaya",
                "email": "emre.kaya@urbanpulse.com",
                "department": "Lojistik",
                "role": "Operasyon Sorumlusu",
                "status": "Aktif",
                "last_login": "Bugun, 09:42",
                "avatar_bg": "#CFE5F4",
            },
            {
                "id": 2,
                "name": "Selin Aksoy",
                "email": "selin.aksoy@urbanpulse.com",
                "department": "Idari Isler",
                "role": "Sistem Yoneticisi",
                "status": "Aktif",
                "last_login": "Dun, 16:15",
                "avatar_bg": "#F4CDD8",
            },
            {
                "id": 3,
                "name": "Murat Demir",
                "email": "murat.demir@urbanpulse.com",
                "department": "Atik Yonetimi",
                "role": "Saha Operatoru",
                "status": "Pasif",
                "last_login": "12.05.2024",
                "avatar_bg": "#E5E5E5",
            },
            {
                "id": 4,
                "name": "Asli Yilmaz",
                "email": "asli.yilmaz@urbanpulse.com",
                "department": "Lojistik",
                "role": "Filo Denetcisi",
                "status": "Aktif",
                "last_login": "3 saat once",
                "avatar_bg": "#CFE5F4",
            },
        ]
        self._next_id = 5

    def get_all(self):
        return [person.copy() for person in self._personnel]

    def add_person(self, person_data):
        new_person = person_data.copy()
        new_person["id"] = self._next_id
        self._next_id += 1

        if "avatar_bg" not in new_person:
            new_person["avatar_bg"] = "#DCEBF6"

        if "last_login" not in new_person or not new_person["last_login"]:
            new_person["last_login"] = "Bugun, 09:00"

        self._personnel.append(new_person)
        return new_person.copy()

    def update_person(self, person_id, updated_data):
        for person in self._personnel:
            if person["id"] == person_id:
                person.update(updated_data)
                return person.copy()
        return None

    def toggle_status(self, person_id):
        for person in self._personnel:
            if person["id"] == person_id:
                person["status"] = "Pasif" if person["status"] == "Aktif" else "Aktif"
                return person.copy()
        return None
