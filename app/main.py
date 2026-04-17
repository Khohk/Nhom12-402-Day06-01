import json
import logging
import signal
import sys
import time
from contextlib import asynccontextmanager
from typing import Optional

from upstash_redis import Redis
from fastapi import Depends, FastAPI, HTTPException, Request
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel

from .auth import verify_api_key
from .config import settings
from .cost_guard import add_cost, check_budget
from .rate_limiter import check_rate_limit

# --- Structured JSON logging ---
class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(_JsonFormatter())
logging.root.handlers = [_handler]
logging.root.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))
logger = logging.getLogger(__name__)

# --- Redis ---
r = Redis(url=settings.UPSTASH_REDIS_REST_URL, token=settings.UPSTASH_REDIS_REST_TOKEN)

# --- Graceful shutdown flag ---
_shutting_down = False


def _handle_sigterm(*_):
    global _shutting_down
    _shutting_down = True
    logger.info("SIGTERM received — graceful shutdown initiated")


signal.signal(signal.SIGTERM, _handle_sigterm)


# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Vinmec AI agent starting up")
    yield
    logger.info("Vinmec AI agent shut down")


app = FastAPI(title="Vinmec AI Agent", lifespan=lifespan)


# --- Request logging middleware ---
@app.middleware("http")
async def _log_requests(request: Request, call_next):
    if _shutting_down:
        raise HTTPException(status_code=503, detail="Server is shutting down")
    start = time.time()
    response = await call_next(request)
    logger.info(json.dumps({
        "event": "request",
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": round((time.time() - start) * 1000, 2),
    }))
    return response


# --- Models ---
class AskRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


class AskResponse(BaseModel):
    answer: str
    session_id: str


# --- Endpoints ---
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    try:
        r.ping()
    except Exception:
        raise HTTPException(status_code=503, detail="Redis unavailable")
    return {"status": "ready", "redis": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(
    body: AskRequest,
    user_id: str = Depends(verify_api_key),
    _rate: None = Depends(check_rate_limit),
    _budget: None = Depends(check_budget),
):
    from agent import graph  # lazy import to keep startup fast

    session_id = body.session_id or user_id
    history_key = f"history:{session_id}"

    # 1. Get conversation history from Redis
    messages = []
    for raw in r.lrange(history_key, 0, -1):
        data = json.loads(raw)
        cls = HumanMessage if data["role"] == "human" else AIMessage
        messages.append(cls(content=data["content"]))
    messages.append(HumanMessage(content=body.question))

    # 2. Call LLM via LangGraph agent
    try:
        result = graph.invoke({"messages": messages})
        answer: str = result["messages"][-1].content
    except Exception as exc:
        logger.error(f"Agent error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Agent error")

    # 3. Persist history to Redis (keep last 20 turns, 24 h TTL)
    r.rpush(history_key, json.dumps({"role": "human", "content": body.question}))
    r.rpush(history_key, json.dumps({"role": "ai", "content": answer}))
    r.ltrim(history_key, -20, -1)
    r.expire(history_key, 86400)

    # 4. Record estimated cost
    add_cost(user_id)

    logger.info(json.dumps({"event": "ask", "user_id": user_id, "session_id": session_id}))
    return AskResponse(answer=answer, session_id=session_id)
