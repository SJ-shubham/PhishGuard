import redis.asyncio as aioredis
from backend.config import get_settings

_settings = get_settings()

_redis: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            _settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis


async def redis_ping() -> bool:
    try:
        return await get_redis().ping()
    except Exception:
        return False
