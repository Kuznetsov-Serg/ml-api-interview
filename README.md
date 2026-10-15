```text
ml_api_interview/
├── app/
│   ├── __init__.py
│   ├── main.py                      # Точка входа FastAPI
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ── predict.py           # Эндпоинты
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                # ✅ Настройки (Pydantic Settings)
│   │   ├── security.py              # Безопасность
│   │   └── exceptions.py            # Кастомные исключения
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                  # ✅ Абстрактный класс
│   │   ├── model_type_a.py          # ✅ Pickle реализация
│   │   └── model_type_b.py          # ✅ JSON реализация
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── predictions.py           # Pydantic схемы
│   ├── services/
│   │   ├── __init__.py
│   │   └── prediction_service.py    # Бизнес-логика
│   └── utils/
│       ├── __init__.py
│       ├── create_dummy_model.py    # ✅ Генерация тестовой модели
│       ├── cache.py                 # Redis cache
│       └── logging_config.py        # Логирование
── data/
│   ├── models/
│   │   └── .gitkeep                 # Placeholder
│   └── input_ml/
│       ├── notebook_ml_1.ipynb
│       ├── notebook_ml_2.ipynb
│       └── notebook_ml_3.ipynb
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # ✅ Pytest fixtures
│   ├── test_health.py
│   ── test_predict.py
├── docker-compose.yml               # ✅
├── Dockerfile                       # ✅
├── .gitignore                       # ✅ 
├── .env.example                     # ✅ Шаблон
├── pyproject.toml                   # Poetry dependencies
├── poetry.lock
└── README.md                        # ✅ Документация
```
