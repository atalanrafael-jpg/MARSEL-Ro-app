import asyncio

import httpx
from .config import settings


class RoAppClient:
    def __init__(self):
        self.base_url = settings.roapp_base_url.rstrip("/")
        self.timeout = settings.roapp_timeout_seconds

    def _headers(self):
        if not settings.roapp_api_key:
            raise RuntimeError("ROAPP_API_KEY не задан")
        return {"Authorization": f"Bearer {settings.roapp_api_key}"}

    async def get_orders(self, page: int = 1):
        if page < 1:
            raise ValueError("page должен быть >= 1")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/orders",
                params={"page": page},
                headers=self._headers(),
            )
            if response.status_code == 429:
                await asyncio.sleep(0.5)
                response = await client.get(
                    f"{self.base_url}/orders",
                    params={"page": page},
                    headers=self._headers(),
                )
            response.raise_for_status()
            return response.json()

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
            if isinstance(count, int) and isinstance(items, list):
                if page * 50 >= count or not items:
                    break
            elif isinstance(items, list) and len(items) < 50:
                break
            else:
                break
        return pages
