# app/utils/create_dummy_models.py
"""
Скрипт для генерации тестовых моделей.
Запускается при сборке Docker-образа.
"""

import json
import pickle
from pathlib import Path

from app.models.dummy_models import DummyPickleModel


def create_dummy_models():
    """Создаёт оба типа dummy-моделей в data/models/."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    model_dir = base_dir / "data" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)

    # 1. Model A — pickle (класс на уровне модуля!)
    model_pickle = DummyPickleModel()
    model_pickle_path = model_dir / "model_pickle.pkl"
    with open(model_pickle_path, "wb") as f:
        pickle.dump(model_pickle, f)
    print(f"✅ Model pickle created: {model_pickle_path}")

    # 2. Model JSON (только данные)
    model_json_data = {
        "name": "DummyJSONModel",
        "version": "1.0",
        "features": ["age", "income", "has_loan", "transaction_count"],
        "type": "mock",
    }
    model_json_path = model_dir / "model_json.json"
    with open(model_json_path, "w", encoding="utf-8") as f:
        json.dump(model_json_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Model JSON created: {model_json_path}")


if __name__ == "__main__":
    create_dummy_models()
