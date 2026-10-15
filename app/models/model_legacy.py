# app/models/model_legacy.py
"""Legacy ML model wrapper (для обратной совместимости)."""
from pathlib import Path
from typing import Any
import joblib
import numpy as np
import pandas as pd
from functools import lru_cache
import structlog

logger = structlog.get_logger()

class MLModel:
    """Обёртка над ML моделью с lazy loading."""

    def __init__(self, model_path: str):
        self._model_path = Path(model_path)
        self._model = None
        self._feature_names = None

    def load(self) -> None:
        """Ленивая загрузка модели."""
        if self._model is not None:
            return
        logger.info("loading_model", path=str(self._model_path))
        self._model = joblib.load(self._model_path)
        if hasattr(self._model, 'feature_names_in_'):
            self._feature_names = list(self._model.feature_names_in_)
        logger.info("model_loaded",
                    type=type(self._model).__name__,
                    features=self._feature_names)

    def predict(self, features: dict[str, Any] | list[dict[str, Any]]) -> Any:
        """Предсказание для одного или батча запросов."""
        if self._model is None:
            self.load()

        if isinstance(features, dict):
            features = [features]

        df = pd.DataFrame(features)
        predictions = self._model.predict(df)
        probabilities = self._model.predict_proba(df)

        return [
            {
                "prediction": int(pred),
                "probability": float(prob.max()),
                "class": self._model.classes_[int(pred)]
            }
            for pred, prob in zip(predictions, probabilities)
        ]

    def health_check(self) -> dict:
        return {
            "model_loaded": self._model is not None,
            "model_type": type(self._model).__name__ if self._model else None,
            "features": self._feature_names
        }

# Singleton
_model_instance: MLModel | None = None

@lru_cache()
def get_model(model_path: str) -> MLModel:
    global _model_instance
    if _model_instance is None:
        _model_instance = MLModel(model_path)
    return _model_instance