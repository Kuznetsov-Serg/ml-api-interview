# app/core/cache.py
import json
import logging

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


async def get_cache(redis_url: str, is_redis: bool) -> aioredis.Redis | None:
    """Создаёт Redis клиент или возвращает None, если кэш отключен/недоступен."""
    if not is_redis:
        logger.info("Redis cache is disabled by configuration")
        return None
    try:
        client = aioredis.from_url(redis_url, decode_responses=True)
        # Проверяем реальное подключение при старте
        await client.ping()
        logger.info("Successfully connected to Redis cache")
        return client
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Failed to connect to Redis: {e}. Cache disabled.")
        return None


async def check_cache(cache: aioredis.Redis, key: str):
    """Проверяет кэш."""
    data = await cache.get(key)
    if data:
        return json.loads(data)
    return None


async def save_to_cache(cache: aioredis.Redis, key: str, value, ttl: int = 3600):
    """Сохраняет в кэш."""
    if hasattr(value, "model_dump"):
        value = value.model_dump()
    await cache.setex(key, ttl, json.dumps(value))
