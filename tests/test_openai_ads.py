from datetime import datetime, timedelta, timezone

import pytest

from app.openai_ads import OpenAIAdsClient, OpenAIAdsContent


def test_order_event_uses_minor_units_and_stable_id(monkeypatch):
    client = OpenAIAdsClient()
    captured = {}

    async def fake_send(events, *, validate_only=None):
        captured["events"] = events
        captured["validate_only"] = validate_only
        return {"ok": True}

    monkeypatch.setattr(client, "send_events", fake_send)
    result = __import__("asyncio").run(
        client.send_order_created(
            order_id="order_123",
            amount_minor=125000,
            currency="RUB",
            contents=[OpenAIAdsContent(id="sku-1", name="Ring", quantity=1)],
            timestamp=datetime.now(timezone.utc),
            source_url="https://marsel.example/checkout/confirmation?utm_source=chatgpt#done",
            validate_only=True,
        )
    )

    assert result == {"ok": True}
    event = captured["events"][0]
    assert event.id == "order_123"
    assert event.type == "order_created"
    assert event.data["amount"] == 125000
    assert event.data["currency"] == "RUB"
    assert event.data["contents"][0]["id"] == "sku-1"
    assert event.source_url == "https://marsel.example/checkout/confirmation"
    assert captured["validate_only"] is True


def test_web_order_requires_source_url():
    client = OpenAIAdsClient()
    with pytest.raises(ValueError, match="source_url"):
        __import__("asyncio").run(
            client.send_order_created(
                order_id="order_123",
                amount_minor=100,
                timestamp=datetime.now(timezone.utc),
            )
        )


def test_source_url_must_be_http_or_https():
    client = OpenAIAdsClient()
    with pytest.raises(ValueError, match="HTTP\(S\)"):
        __import__("asyncio").run(
            client.send_order_created(
                order_id="order_123",
                amount_minor=100,
                source_url="javascript:alert(1)",
            )
        )


def test_order_amount_cannot_be_negative():
    client = OpenAIAdsClient()
    with pytest.raises(ValueError, match="отрицательным"):
        __import__("asyncio").run(
            client.send_order_created(
                order_id="order_123",
                amount_minor=-1,
                source_url="https://marsel.example/checkout/confirmation",
            )
        )


def test_order_timestamp_must_be_recent():
    client = OpenAIAdsClient()
    with pytest.raises(ValueError, match="7 дней"):
        __import__("asyncio").run(
            client.send_order_created(
                order_id="order_123",
                amount_minor=100,
                timestamp=datetime.now(timezone.utc) - timedelta(days=8),
                source_url="https://marsel.example/checkout/confirmation",
            )
        )
