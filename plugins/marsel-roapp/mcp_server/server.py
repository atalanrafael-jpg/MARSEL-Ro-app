from __future__ import annotations

import asyncio
import os
from collections import Counter
from typing import Any

import httpx
from mcp.server.mcpserver import MCPServer

BASE_URL = os.getenv("ROAPP_BASE_URL", "https://api.roapp.io/v2").rstrip("/")
MAX_RETRIES = 3
RETRYABLE = {408, 425, 429, 500, 502, 503, 504}

GET_ORDERS_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": True,
}

AUDIT_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "pages_scanned": {"type": "integer", "minimum": 0},
        "orders_scanned": {"type": "integer", "minimum": 0},
        "identifiers_found": {"type": "integer", "minimum": 0},
        "duplicate_identifiers": {"type": "array", "items": {"type": "string"}},
        "missing_common_fields": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "minimum": 0},
                "status": {"type": "integer", "minimum": 0},
            },
            "required": ["id", "status"],
            "additionalProperties": False,
        },
        "read_only": {"type": "boolean", "const": True},
    },
    "required": [
        "pages_scanned",
        "orders_scanned",
        "identifiers_found",
        "duplicate_identifiers",
        "missing_common_fields",
        "read_only",
    ],
    "additionalProperties": False,
}

CONNECTOR_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["ready", "not_configured"]},
        "roapp_api_base_configured": {"type": "boolean"},
        "roapp_api_key_configured": {"type": "boolean"},
        "read_only": {"type": "boolean", "const": True},
    },
    "required": [
        "status",
        "roapp_api_base_configured",
        "roapp_api_key_configured",
        "read_only",
    ],
    "additionalProperties": False,
}

mcp = MCPServer(
    "MARSEL RO App",
    instructions=(
        "Read-only MARSEL RO App inspection. Fetch orders, run bounded data-quality audits, "
        "and report connector readiness. Never mutate upstream data."
    ),
)


def _headers() -> dict[str, str]:
    token = os.getenv("ROAPP_API_KEY", "")
    if not token:
        raise RuntimeError("ROAPP_API_KEY is not configured")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "MARSEL-RoApp-Plugin/1.2",
    }


async def _get(path: str, params: dict[str, Any] | None = None) -> Any:
    timeout = float(os.getenv("ROAPP_TIMEOUT_SECONDS", "30"))
    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = await client.get(
                    f"{BASE_URL}/{path.lstrip('/')}", params=params, headers=_headers()
                )
                if response.status_code not in RETRYABLE:
                    response.raise_for_status()
                    return response.json()
                if attempt >= MAX_RETRIES:
                    response.raise_for_status()
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                if attempt >= MAX_RETRIES:
                    raise RuntimeError(f"RO App API network error: {exc}") from exc
            await asyncio.sleep(min(0.75 * (2**attempt), 8))
    raise RuntimeError("RO App API request failed")


def _records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in ("data", "items", "orders", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
    return []


def _identifier(record: dict[str, Any]) -> str | None:
    for field in ("id", "uuid", "number", "order_id", "order_number"):
        value = record.get(field)
        if value not in (None, ""):
            return str(value)
    return None


def _audit(pages: list[Any]) -> dict[str, Any]:
    records = [r for page in pages for r in _records(page)]
    ids = [x for x in (_identifier(r) for r in records) if x is not None]
    duplicates = sorted(x for x, n in Counter(ids).items() if n > 1)
    return {
        "pages_scanned": len(pages),
        "orders_scanned": len(records),
        "identifiers_found": len(ids),
        "duplicate_identifiers": duplicates,
        "missing_common_fields": {
            field: sum(1 for r in records if r.get(field) in (None, ""))
            for field in ("id", "status")
        },
        "read_only": True,
    }


@mcp.tool(
    annotations={"title": "Get RO App orders", "readOnlyHint": True},
    output_schema=GET_ORDERS_OUTPUT_SCHEMA,
)
async def get_orders(page: int = 1) -> dict[str, Any]:
    """Fetch one RO App orders page without modifying data."""
    if page < 1:
        raise ValueError("page must be >= 1")
    return await _get("orders", {"page": page})


@mcp.tool(
    annotations={"title": "Audit RO App orders", "readOnlyHint": True},
    output_schema=AUDIT_OUTPUT_SCHEMA,
)
async def audit_orders(max_pages: int = 10) -> dict[str, Any]:
    """Run a bounded read-only order audit across 1-100 pages."""
    if not 1 <= max_pages <= 100:
        raise ValueError("max_pages must be between 1 and 100")
    pages: list[Any] = []
    for page in range(1, max_pages + 1):
        payload = await _get("orders", {"page": page})
        pages.append(payload)
        items = _records(payload)
        if not items or len(items) < 50:
            break
        count = payload.get("count") if isinstance(payload, dict) else None
        if isinstance(count, int) and page * len(items) >= count:
            break
    return _audit(pages)


@mcp.tool(
    annotations={"title": "Check connector readiness", "readOnlyHint": True},
    output_schema=CONNECTOR_OUTPUT_SCHEMA,
)
def connector_readiness() -> dict[str, Any]:
    """Report non-secret configuration state without contacting RO App."""
    key = bool(os.getenv("ROAPP_API_KEY"))
    return {
        "status": "ready" if key else "not_configured",
        "roapp_api_base_configured": bool(BASE_URL),
        "roapp_api_key_configured": key,
        "read_only": True,
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http", stateless_http=True, json_response=True)
