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
            response.raise_for_status()
            return response.json()
