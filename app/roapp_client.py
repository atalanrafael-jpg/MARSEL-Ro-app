import asyncio
import random
from typing import Any

import httpx
from .config import settings


class RoAppClient:
    """Read-only RO App API client used by the audit layer."""

    RETRYABLE_STATUS_CODES = {408, 425, 429, 500, 502, 503, 504}

    def __init__(self):
        self.base_url = settings.roapp_base_url.rstrip("/")
        self.timeout = settings.roapp_timeout_seconds
        self.max_retries = settings.roapp_max_retries
        self.retry_base_seconds = settings.roapp_retry_base_seconds

    def _headers(self) -> dict[str, str]:
        if not settings.roapp_api_key:
            raise RuntimeError("ROAPP_API_KEY не задан")
        return {
            "Authorization": f"Bearer {settings.roapp_api_key}",
            "Accept": "application/json",
            "User-Agent": "MARSEL-RoApp-Audit/1.0",
        }

    async def _get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retries + 1):
                try:
                    response = await client.get(url, params=params, headers=self._headers())
                    if response.status_code not in self.RETRYABLE_STATUS_CODES:
                        response.raise_for_status()
                        return response.json()
                    if attempt >= self.max_retries:
                        response.raise_for_status()
                    retry_after = response.headers.get("Retry-After")
                    try:
                        delay = float(retry_after) if retry_after else self.retry_base_seconds * (2**attempt)
                    except ValueError:
                        delay = self.retry_base_seconds * (2**attempt)
                    await asyncio.sleep(max(0.0, min(delay, 30.0)) + random.uniform(0, 0.25))
                except (httpx.TimeoutException, httpx.NetworkError) as exc:
                    if attempt >= self.max_retries:
                        raise RuntimeError(f"RO App API network error: {exc}") from exc
                    delay = self.retry_base_seconds * (2**attempt)
                    await asyncio.sleep(delay + random.uniform(0, 0.25))
        raise RuntimeError("RO App API request failed without a response")

    async def get_orders(self, page: int = 1):
        if page < 1:
            raise ValueError("page должен быть >= 1")
        return await self._get("orders", params={"page": page})

    async def get_orders_pages(self, max_pages: int = 10):
        if max_pages < 1 or max_pages > 100:
            raise ValueError("max_pages должен быть от 1 до 100")
        pages = []
        for page in range(1, max_pages + 1):
            payload = await self.get_orders(page)
            pages.append(payload)
            if not isinstance(payload, dict):
                break
            count = payload.get("count")
            items = payload.get("data") or payload.get("items") or payload.get("orders")
            if not isinstance(items, list) or not items:
                break
            if isinstance(count, int) and page * len(items) >= count:
                break
            if len(items) < 50:
                break
        return pages
