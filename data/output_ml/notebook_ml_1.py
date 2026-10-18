# data/output_ml/notebook_ml_1.py
"""
Оптимизированная версия notebook_ml_1.py
- Векторизация вместо iterrows
- Lazy loading модели
- Pydantic валидация
- Pipeline для согласованности признаков
"""

import logging
import joblib
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer


# 1. Типизация входных данных (Pydantic Schema)
class CustomerData(BaseModel):
    age: int = Field(ge=18, le=120, description="Возраст клиента")
    income: float = Field(ge=0.0, description="Доход")
    has_loan: bool = Field(description="Наличие кредита")


# 2. Функция feature engineering (векторизованная)
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Векторизованное вычисление признаков.
    Гарантирует 100% идентичность выходного DataFrame со старой версией.
    """
    df = df.copy()
    # 1. Базовый расчет скоринга (векторизованно)
    df["risk_score"] = (df["age"] * 0.3) + (df["income"] * 0.7)
    # 2. Добавляем 10, если has_loan == 'yes' (векторизованная замена if в цикле)
    # np.where(condition, value_if_true, value_if_false)
    df["risk_score"] = np.where(
        df["has_loan"] == "yes", df["risk_score"] + 10, df["risk_score"]
    )
    return df


# 3. Lazy Loading модели с Pipeline
class ModelService:
    def __init__(self, model_path: str = "model.pkl"):
        self.model_path = model_path
        self._pipeline = None
        self._logger = logging.getLogger(__name__)

    @property
    def pipeline(self):
        if self._pipeline is None:
            self._logger.info("Loading model from disk...")
            self._pipeline = joblib.load(self.model_path)
        return self._pipeline

    def predict(self, data: CustomerData) -> dict:
        """Предсказание для одного клиента."""
        df = pd.DataFrame([data.model_dump()])
        # Преобразуем has_loan в строку для совместимости с обучением
        df["has_loan"] = df["has_loan"].map({True: "yes", False: "no"})

        prediction = self.pipeline.predict(df)[0]
        probability = self.pipeline.predict_proba(df)[0].max()
        return {"prediction": int(prediction), "probability": float(probability)}


# 4. Обучение с Pipeline
def train_and_save_model(csv_path: str, output_path: str):
    try:
        df = pd.read_csv(csv_path)

        # Разделение на train/test ДО трансформации
        X = df[["age", "income", "has_loan", "churn"]]
        X_train, X_test, y_train, y_test = train_test_split(
            X[["age", "income", "has_loan"]], X["churn"], test_size=0.2, random_state=42
        )

        # Создаём Pipeline: feature engineering + модель
        pipeline = Pipeline(
            [
                ("features", FunctionTransformer(engineer_features)),
                ("model", RandomForestClassifier(n_estimators=100, random_state=42)),
            ]
        )

        pipeline.fit(X_train, y_train)

        acc = accuracy_score(y_test, pipeline.predict(X_test))
        logging.info(f"Model trained successfully. Accuracy: {acc:.4f}")

        joblib.dump(pipeline, output_path)
        logging.info(f"Pipeline saved to {output_path}")

    except FileNotFoundError as e:
        logging.error(f"Data file not found: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error during training: {e}")
        raise


# Пример использования
if __name__ == "__main__":
    # Обучение
    train_and_save_model("../customers.csv", "model_pipeline_1.pkl")

    # Инференс
    service = ModelService("model_pipeline_1.pkl")
    result = service.predict(CustomerData(age=30, income=50000.0, has_loan=False))
    print(f"Prediction: {result}")
