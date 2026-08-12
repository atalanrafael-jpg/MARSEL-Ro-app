import pytest
import httpx

from app.roapp_client import RoAppClient


@pytest.mark.asyncio
async def test_orders_retries_429(monkeypatch):
    client = RoAppClient()
    client.max_retries = 1
    client.retry_base_seconds = 0
    calls = 0

    from app.config import settings
    original_key = settings.roapp_api_key
    settings.roapp_api_key = "test-key"
    try:
        class FakeResponse:
            def __init__(self, status_code, payload):
                self.status_code = status_code
                self.headers = {}
                self._payload = payload

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise httpx.HTTPStatusError("error", request=None, response=self)

            def json(self):
                return self._payload

        class FakeAsyncClient:
            def __init__(self, *args, **kwargs):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                return False

            async def get(self, *args, **kwargs):
                nonlocal calls
                calls += 1
                if calls == 1:
                    return FakeResponse(429, {})
                return FakeResponse(200, {"count": 0, "data": []})

        monkeypatch.setattr("app.roapp_client.httpx.AsyncClient", FakeAsyncClient)
        result = await client.get_orders(1)
        assert result == {"count": 0, "data": []}
        assert calls == 2
    finally:
        settings.roapp_api_key = original_key


@pytest.mark.asyncio
async def test_missing_api_key_is_rejected():
    client = RoAppClient()
    from app.config import settings
    original = settings.roapp_api_key
    settings.roapp_api_key = ""
    try:
        with pytest.raises(RuntimeError, match="ROAPP_API_KEY"):
            await client.get_orders(1)
    finally:
        settings.roapp_api_key = original


@pytest.mark.asyncio
async def test_pagination_stops_on_short_page(monkeypatch):
    client = RoAppClient()
    calls = []

    async def fake_get_orders(page):
        calls.append(page)
        return {"count": 3, "data": [{"id": i} for i in range(3)]}

    monkeypatch.setattr(client, "get_orders", fake_get_orders)
    pages = await client.get_orders_pages(100)
    assert len(pages) == 1
    assert calls == [1]


def test_configured_rate_limit_cannot_exceed_documented_ceiling(monkeypatch):
    from app.config import settings
    original = settings.roapp_max_requests_per_second
    settings.roapp_max_requests_per_second = 100
    try:
        client = RoAppClient()
        assert client.max_requests_per_second == 3
    finally:
        settings.roapp_max_requests_per_second = original
