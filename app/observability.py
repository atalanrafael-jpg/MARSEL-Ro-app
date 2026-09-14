from __future__ import annotations

import json
import logging
import time
import uuid
from contextvars import ContextVar
from typing import Any

from fastapi import Request
from starlette.responses import Response


logger = logging.getLogger("marsel.observability")
_correlation_id: ContextVar[str | None] = ContextVar("marsel_correlation_id", default=None)

SENSITIVE_HEADERS = {
    "authorization",
    "cookie",
    "set-cookie",
    "x-marsel-api-key",
    "x-api-key",
}


def new_request_id() -> str:
    return str(uuid.uuid4())


def get_correlation_id() -> str | None:
    return _correlation_id.get()


def _safe_actor(request: Request) -> str:
    return request.headers.get("x-marsel-actor", "anonymous")[:128]


def _emit(payload: dict[str, Any]) -> None:
    # Structured JSON is intentionally limited to telemetry metadata.
    logger.info(json.dumps(payload, sort_keys=True, separators=(",", ":")))


async def observability_middleware(request: Request, call_next) -> Response:
    request_id = request.headers.get("x-request-id") or new_request_id()
    correlation_id = request.headers.get("x-correlation-id") or request_id
    token = _correlation_id.set(correlation_id)
    started = time.perf_counter()
    response: Response | None = None
    error_class: str | None = None

    try:
        response = await call_next(request)
        return response
    except Exception:
        error_class = "INTERNAL"
        raise
    finally:
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        status = response.status_code if response is not None else 500
        result_status = "success" if status < 400 else "error"
        _emit(
            {
                "request_id": request_id,
                "correlation_id": correlation_id,
                "integration": "marsel-roapp-connector",
                "endpoint": request.url.path,
                "latency_ms": latency_ms,
                "http_status": status,
                "result_status": result_status,
                "retry_count": 0,
                "rate_limit_state": "unknown",
                "error_class": error_class,
                "actor": _safe_actor(request),
                "evidence_id": None,
            }
        )
        if response is not None:
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Correlation-ID"] = correlation_id
        _correlation_id.reset(token)
