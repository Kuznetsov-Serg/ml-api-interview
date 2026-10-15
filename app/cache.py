import json
import redis.asyncio as aioredis

async def get_cache(redis_url: str) -> aioredis.Redis:
    return aioredis.from_url(redis_url, decode_responses=True)

async def check_cache(cache: aioredis.Redis, key: str):
    data = await cache.get(key)
    if data:
        return json.loads(data)
    return None

async def save_to_cache(cache: aioredis.Redis, key: str, value, ttl: int = 3600):
    await cache.setex(key, ttl, json.dumps(value.model_dump() if hasattr(value, 'model_dump') else value))