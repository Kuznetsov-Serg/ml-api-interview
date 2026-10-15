# app/models/dummy_models.py
"""
Dummy models для тестирования API.
Классы должны быть на уровне модуля, чтобы pickle мог их десериализовать.
"""


class DummyPickleModel:
    """Заглушка модели для Model Type A (pickle)."""

    def __init__(self):
        self.name = "DummyPickleModel"
        self.version = "1.0"
        self.features = ["age", "income", "has_loan", "transaction_count"]

    def predict(self, data):
        """Имитация предсказания."""
        # data может быть list или dict
        if isinstance(data, list):
            data = data[0] if data else {}

        age = data.get("age", 0)
        income = data.get("income", 0)

        # Простая "логика" для демонстрации
        probability = min(0.99, max(0.01, (age / 100) * 0.5 + (income / 100000) * 0.5))
        prediction = 1 if probability > 0.5 else 0

        return {
            "prediction": prediction,
            "probability": round(probability, 4),
            "class": "HighRisk" if prediction == 1 else "LowRisk",
        }

    def __repr__(self):
        return f"DummyPickleModel(name={self.name}, version={self.version})"