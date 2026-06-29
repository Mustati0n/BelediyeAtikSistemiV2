class ContainerService:
    def __init__(self):
        self._containers = [
            {
                "id": 1,
                "code": "KNT-1001",
                "region": "Merkez Bolge",
                "fill_rate": 92,
                "status": "Kritik",
                "lat": "40.9912",
                "lng": "29.0277",
            },
            {
                "id": 2,
                "code": "KNT-1002",
                "region": "Kuzey Bolge",
                "fill_rate": 68,
                "status": "Izleniyor",
                "lat": "41.0154",
                "lng": "28.9795",
            },
            {
                "id": 3,
                "code": "KNT-1003",
                "region": "Guney Bolge",
                "fill_rate": 24,
                "status": "Normal",
                "lat": "40.9781",
                "lng": "29.1024",
            },
            {
                "id": 4,
                "code": "KNT-1004",
                "region": "Dogu Bolge",
                "fill_rate": 100,
                "status": "Goreve Atandi",
                "lat": "40.9978",
                "lng": "29.1452",
            },
        ]
        self._next_id = 5

    def get_all(self):
        return [container.copy() for container in self._containers]

    def add_container(self, container_data):
        new_container = container_data.copy()
        new_container["id"] = self._next_id
        self._next_id += 1
        self._containers.append(new_container)
        return new_container.copy()

    def update_container(self, container_id, updated_data):
        for container in self._containers:
            if container["id"] == container_id:
                container.update(updated_data)
                return container.copy()
        return None

    def delete_container(self, container_id):
        for index, container in enumerate(self._containers):
            if container["id"] == container_id:
                deleted = self._containers.pop(index)
                return deleted.copy()
        return None

    def cycle_status(self, container_id):
        order = ["Normal", "Izleniyor", "Kritik", "Goreve Atandi", "Bosaltildi"]
        for container in self._containers:
            if container["id"] == container_id:
                current = container["status"]
                next_index = (order.index(current) + 1) % len(order)
                container["status"] = order[next_index]
                return container.copy()
        return None
