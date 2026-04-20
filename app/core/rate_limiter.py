import time
from collections import defaultdict
from fastapi import Request, HTTPException
from app.core.logger import get_logger
from app.core.config import RATE_LIMIT_MAX, RATE_LIMIT_WINDOW

logger = get_logger("rate_limiter")

# ─── Config ──────────────────────────────────────────────────────
RATE_LIMIT = RATE_LIMIT_MAX
RATE_WINDOW = RATE_LIMIT_WINDOW

# ─── In-memory store: IP -> list of timestamps ───────────────────
_request_log: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(request: Request):
    """
    Rate limiter dependency for FastAPI.
    Allows RATE_LIMIT requests per RATE_WINDOW seconds per IP.
    Raises HTTP 429 if exceeded.
    """
    client_ip = request.client.host
    now = time.time()
    cutoff = now - RATE_WINDOW

    # Clean old entries
    _request_log[client_ip] = [
        t for t in _request_log[client_ip] if t > cutoff
    ]

    if len(_request_log[client_ip]) >= RATE_LIMIT:
        wait = int(RATE_WINDOW - (now - _request_log[client_ip][0])) + 1
        logger.warning(f"⚠️ Rate limit hit for {client_ip} — {len(_request_log[client_ip])} requests in {RATE_WINDOW}s")
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Too many requests",
                "message": f"You can make {RATE_LIMIT} predictions per minute. Please wait {wait}s.",
                "retry_after": wait
            }
        )

    _request_log[client_ip].append(now)
    logger.info(f"✅ Rate check OK for {client_ip} — {len(_request_log[client_ip])}/{RATE_LIMIT} used")
