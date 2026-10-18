# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.6
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---
#
# %% [raw]
# notebook_ml.ipynb — "сырой" код от ML-инженера
# Вариант 1: Scklearn классификатор (самый вероятный)
# Оптимизировать:
# - interows() - оптимизация Pandas
# - загрузка модели в каждом запросе - lazy loading в lifespan
# - нет типизации - pydantic schema
# - нет обработки ошибок
#
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    # Feature engineering (ПЛОХО: iterrows)
    features = []
    for idx, row in df.iterrows():
        age = row["age"]
        income = row["income"]
        score = age * 0.3 + income * 0.7
        if row["has_loan"] == "yes":
            score += 10
        features.append(score)
    df["risk_score"] = features
    return df


def train_and_save_model(csv_path: str, output_path: str):
    # Загрузка данных
    df = pd.read_csv("../customers.csv")

    # Обучение
    df = pd.read_csv(csv_path)
    df = engineer_features(df)

    X = df[["age", "income", "risk_score"]]
    y = df["churn"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)
    print("Accuracy:", accuracy_score(y_test, model.predict(X_test)))

    # Сохранение
    joblib.dump(model, "model_1.pkl")


if __name__ == "__main__":
    train_and_save_model("../customers.csv", "model_1.pkl")
