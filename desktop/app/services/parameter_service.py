class ParameterService:
    def __init__(self):
        self._parameters = {
            "salary_base_multiplier": 1.20,
            "child_additional_payment": 750.00,
            "critical_fill_threshold": 85,
            "plastic_unit_price": 6.50,
            "glass_unit_price": 2.75,
            "metal_unit_price": 8.40,
            "paper_unit_price": 3.20,
            "organic_unit_price": 1.10,
            "other_unit_price": 0.90,
        }

    def get_all(self):
        return self._parameters.copy()

    def update_all(self, updated_data):
        self._parameters.update(updated_data)
        return self._parameters.copy()

    def reset_defaults(self):
        self._parameters = {
            "salary_base_multiplier": 1.20,
            "child_additional_payment": 750.00,
            "critical_fill_threshold": 85,
            "plastic_unit_price": 6.50,
            "glass_unit_price": 2.75,
            "metal_unit_price": 8.40,
            "paper_unit_price": 3.20,
            "organic_unit_price": 1.10,
            "other_unit_price": 0.90,
        }
        return self._parameters.copy()
