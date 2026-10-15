# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "ML Prediction API"
    ENV: str = "development"

    # Model
    MODEL_TYPE: str = "type_pickle"  # "type_pickle" или "type_json"
    # Базовые пути. Будут перезаписаны в main.py в зависимости от MODEL_TYPE
    MODEL_PATH_PICKLE: str = "./data/models/model_pickle.pkl"
    MODEL_PATH_JSON: str = "./data/models/model_json.json"

    # PostgreSQL
    DATABASE_URL: str = "postgresql+asyncpg://ml_user:ml_pass@db:5432/ml_db"

    # RedisF
    REDIS_URL: str = "redis://redis:6379/0"
    CACHE_TTL: int = 3600

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()