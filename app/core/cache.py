# app/core/cache.py
import json

import redis.asyncio as aioredis


async def get_cache(redis_url: str) -> aioredis.Redis:
    """Создаёт Redis клиент."""
    return aioredis.from_url(redis_url, decode_responses=True)


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
