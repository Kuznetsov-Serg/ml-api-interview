# app/models/model_pickle.py
"""
Model Type PICKLE — загрузка через pickle.
"""

import pickle

from .base import BaseModelInterface
from .dummy_models import DummyPickleModel  # Импортируем класс!


class SideModelPickle(BaseModelInterface):
    def __init__(self):
        self.model = None

    def load(self, path: str) -> None:
        """Загружает pickle-модель."""
        with open(path, "rb") as f:
            self.model = pickle.load(f)

        # Проверка типа (опционально)
        if not isinstance(self.model, DummyPickleModel):
            raise TypeError(f"Expected DummyPickleModel, got {type(self.model)}")

    def predict(self, data: dict) -> dict:
        """Вызывает predict у загруженной модели."""
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() first.")

        result = self.model.predict(data)
        return {
            "model_type": "PICKLE",
            "model_name": self.model.name,
            "model_version": self.model.version,
            **result,
        }
