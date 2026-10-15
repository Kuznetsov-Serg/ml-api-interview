# app/utils/create_dummy_models.py
"""
Скрипт для генерации тестовых моделей.
Запускается при сборке Docker-образа.
"""
import pickle
import json
from pathlib import Path
from app.models.dummy_models import DummyPickleModel


def create_dummy_models():
    """Создаёт оба типа dummy-моделей в data/models/."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    model_dir = base_dir / "data" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)

    # 1. Model A — pickle (класс на уровне модуля!)
    model_a = DummyPickleModel()
    model_a_path = model_dir / "model_a.pkl"
    with open(model_a_path, "wb") as f:
        pickle.dump(model_a, f)
    print(f"✅ Model A (pickle) created: {model_a_path}")

    # 2. Model B — JSON (только данные)
    model_b_data = {
        "name": "DummyJSONModel",
        "version": "1.0",
        "features": ["age", "income", "has_loan", "transaction_count"],
        "type": "mock",
    }
    model_b_path = model_dir / "model_b.json"
    with open(model_b_path, "w", encoding="utf-8") as f:
        json.dump(model_b_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Model B (JSON) created: {model_b_path}")


if __name__ == "__main__":
    create_dummy_models()