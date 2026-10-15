# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "ML Prediction API"
    ENV: str = "development"

    # Model
    MODEL_TYPE: str = "type_a"  # "type_a" или "type_b"
    # Базовые пути. Будут перезаписаны в main.py в зависимости от MODEL_TYPE
    MODEL_PATH_A: str = "./data/models/model_a.pkl"
    MODEL_PATH_B: str = "./data/models/model_b.json"

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