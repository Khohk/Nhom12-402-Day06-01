from datetime import datetime

import redis
from fastapi import Depends, HTTPException

from .auth import verify_api_key
from .config import settings

_r = None

def _redis():
    global _r
    if _r is None:
        _r = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _r

# GPT-4o-mini average cost estimate per request (~500 input + 200 output tokens)
COST_PER_REQUEST_USD = 0.0003


def _budget_key(user_id: str) -> str:
    month = datetime.now().strftime("%Y-%m")
    return f"budget:{user_id}:{month}"


def check_budget(user_id: str = Depends(verify_api_key)) -> None:
    key = _budget_key(user_id)
    spent = float(_redis().get(key) or 0)
    if spent >= settings.MONTHLY_BUDGET_USD:
        raise HTTPException(
            status_code=402,
            detail=f"Monthly budget of ${settings.MONTHLY_BUDGET_USD} exceeded.",
        )


def add_cost(user_id: str, cost_usd: float = COST_PER_REQUEST_USD) -> None:
    key = _budget_key(user_id)
    _redis().incrbyfloat(key, cost_usd)
    _redis().expire(key, 35 * 24 * 3600)  # auto-expire after 35 days
