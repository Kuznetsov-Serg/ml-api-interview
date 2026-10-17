# app/config.py
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "ML Prediction API"
    ENV: str = Field(default="development")

    # Model
    MODEL_TYPE: str = "type_pickle"  # "type_pickle" или "type_json"
    # Базовые пути. Будут перезаписаны в main.py в зависимости от MODEL_TYPE
    MODEL_PATH_PICKLE: str = "./data/models/model_pickle.pkl"
    MODEL_PATH_JSON: str = "./data/models/model_json.json"

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://localhost:5432/ml_db",
        description="URL подключения к PostgreSQL",
    )

    # Redis
    IS_REDIS: bool = Field(
        default=True, description="Использовать Redis (для кэширования)"
    )
    REDIS_URL: str = Field(
        default="redis://redis:6379/0", description="URL подключения к Redis"
    )
    CACHE_TTL: int = 3600

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
