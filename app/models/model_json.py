# app/models/model_json.py
"""
Model Type JSON — загрузка через JSON (безопасный текстовый формат).
"""
import json
from .base import BaseModelInterface


class SideModelJSON(BaseModelInterface):
    def __init__(self):
        self.model_data = None

    def load(self, path: str) -> None:
        """Загружает JSON-модель (только данные, без кода)."""
        with open(path, "r", encoding="utf-8") as f:
            self.model_data = json.load(f)

    def predict(self, data: dict) -> dict:
        """Имитация предсказания на основе JSON-данных."""
        if self.model_data is None:
            raise RuntimeError("Model not loaded. Call load() first.")

        age = data.get("age", 0)
        income = data.get("income", 0)

        probability = min(0.99, max(0.01, (age / 100) * 0.4 + (income / 100000) * 0.6))
        prediction = 1 if probability > 0.5 else 0

        return {
            "model_type": "JSON",
            "model_name": self.model_data.get("name", "Unknown"),
            "model_version": self.model_data.get("version", "1.0"),
            "prediction": prediction,
            "probability": round(probability, 4),
            "class": "HighRisk" if prediction == 1 else "LowRisk",
        }