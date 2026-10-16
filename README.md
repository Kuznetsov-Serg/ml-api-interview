```text
ml_api_interview/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Точка входа FastAPI
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Настройки (Pydantic Settings)
│   │   ├── db.py                  # ← db.py (подключение к PostgreSQL)
│   │   └── cache.py               # ← cache.py (Redis утилиты)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                # Абстрактный базовый класс
│   │   ├── model_type_a.py        # Pickle реализация
│   │   ├── model_type_b.py        # JSON реализация
│   │   └── legacy_model.py        # ← model.py (старая обёртка, для совместимости)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── predictions.py         # Pydantic схемы
│   └── utils/
│       ├── __init__.py
│       └── create_dummy_models.py # Генерация тестовых моделей
── data/
│   ├── input_ml/                  # ← notebook_ml_1.ipynb, notebook_ml_2.ipynb
│   │   ├── notebook_ml_1.ipynb
│   │   └── notebook_ml_2.ipynb
│   └── models/                    # model.pkl, model.json (генерируются скриптом)
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_health.py
│   └── test_predict.py
├── .dockerignore
├── .env
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── main.py                        # Корневой main.py для uvicorn
├── requirements.txt
└── README.md
```

```bash
# Установить плагин (один раз)
poetry self add poetry-plugin-export

# Экспортировать только основные зависимости (без dev)
poetry export -f requirements.txt --output requirements.txt --without-hashes

# Со всеми зависимостями (включая dev)
poetry export -f requirements.txt --output requirements.txt --with dev --without-hashes

# Только основная группа
poetry export -f requirements.txt --output requirements.txt --only main --without-hashes
```
