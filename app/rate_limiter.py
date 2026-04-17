import time

from fastapi import Depends, HTTPException
from upstash_redis import Redis

from .auth import verify_api_key
from .config import settings

_r = None


def _redis() -> Redis:
    global _r
    if _r is None:
        _r = Redis(url=settings.UPSTASH_REDIS_REST_URL, token=settings.UPSTASH_REDIS_REST_TOKEN)
    return _r


def check_rate_limit(user_id: str = Depends(verify_api_key)) -> None:
    key = f"rate:{user_id}"
    now = time.time()
    window = 60  # 1 minute sliding window

    pipe = _redis().pipeline()
    pipe.zremrangebyscore(key, 0, now - window)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, window)
    _, _, count, _ = pipe.execute()

    if count > settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
