# scripts/generate_test_data_customer.py
import numpy as np
import pandas as pd

# Генерируем 100 000 записей для наглядности разницы в скорости
np.random.seed(42)
n_samples = 100_000

df = pd.DataFrame(
    {
        "age": np.random.randint(18, 70, n_samples),
        "income": np.random.normal(50000, 15000, n_samples).clip(min=0).round(2),
        "has_loan": np.random.choice(["yes", "no"], n_samples, p=[0.3, 0.7]),
        "transaction_count": np.random.randint(0, 50, n_samples),
        "churn": np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
    }
)

# Сохраняем в ту же папку
df.to_csv("../data/customers.csv", index=False)
print(f"✅ Файл customers.csv успешно создан ({n_samples} записей)")
