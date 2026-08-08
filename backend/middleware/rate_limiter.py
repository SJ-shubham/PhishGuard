from fastapi import HTTPException, status
from backend.redis_client import get_redis
from backend.config import get_settings

_settings = get_settings()


async def check_scan_rate_limit(user_id: str) -> None:
    """
    Allows up to RATE_LIMIT_SCANS_PER_MINUTE scans per user per minute.
    Uses Redis counter with 60-second TTL.
    Silently skips if Redis is unavailable.
    """
    try:
        key   = f"ratelimit:scan:{user_id}"
        redis = get_redis()
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, 60)

        limit = _settings.rate_limit_scans_per_minute
        if count > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {limit} scans per minute allowed.",
                headers={"Retry-After": "60"},
            )
    except HTTPException:
        raise
    except Exception:
        pass  # Redis down — skip rate limiting
