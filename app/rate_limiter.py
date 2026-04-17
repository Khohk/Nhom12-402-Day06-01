import time

import redis
from fastapi import Depends, HTTPException

from .auth import verify_api_key
from .config import settings

r = redis.from_url(settings.REDIS_URL, decode_responses=True)


def check_rate_limit(user_id: str = Depends(verify_api_key)) -> None:
    key = f"rate:{user_id}"
    now = time.time()
    window = 60  # 1 minute sliding window

    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, now - window)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, window)
    _, _, count, _ = pipe.execute()

    if count > settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
