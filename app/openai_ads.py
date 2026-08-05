from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from pydantic import BaseModel, Field

from .config import settings


class OpenAIAdsContent(BaseModel):
    id: str
    name: str | None = None
    content_type: str = "product"
    quantity: int = Field(ge=1)


class OpenAIAdsEvent(BaseModel):
    id: str
    type: str = "order_created"
    timestamp_ms: int
    data: dict[str, Any]
    oppref: str | None = None
    source_url: str | None = None
    action_source: str = "web"
    user: dict[str, Any] | None = None
    opt_out: bool = False


class OpenAIAdsEventsRequest(BaseModel):
    validate_only: bool = True
    events: list[OpenAIAdsEvent] = Field(min_length=1, max_length=1000)


class OpenAIAdsClient:
    """Server-side client for OpenAI Ads Conversions API.

    Credentials are read only from environment-backed settings. The conversion
    API key must be generated in Ads Manager > Conversions; it must never be
    exposed to browser/client code.
    """

    def __init__(self) -> None:
        self.base_url = settings.openai_ads_base_url.rstrip("/")
        self.pixel_id = settings.openai_ads_pixel_id
        self.api_key = settings.openai_ads_conversions_api_key
        self.timeout = settings.openai_ads_timeout_seconds

    def _validate_config(self) -> None:
        if not self.pixel_id:
            raise RuntimeError("OPENAI_ADS_PIXEL_ID не задан")
        if not self.api_key:
            raise RuntimeError("OPENAI_ADS_CONVERSIONS_API_KEY не задан")

    @staticmethod
    def _validate_timestamp(timestamp: datetime) -> None:
        now = datetime.now(timezone.utc)
        event_time = timestamp.astimezone(timezone.utc)
        if event_time < now - timedelta(days=7):
            raise ValueError("timestamp события не может быть старше 7 дней")
        if event_time > now + timedelta(minutes=10):
            raise ValueError("timestamp события не может быть более чем на 10 минут в будущем")

    async def send_events(
        self,
        events: list[OpenAIAdsEvent],
        *,
        validate_only: bool | None = None,
    ) -> dict[str, Any]:
        self._validate_config()
        if not 1 <= len(events) <= 1000:
            raise ValueError("OpenAI Ads принимает от 1 до 1000 событий за запрос")

        request = OpenAIAdsEventsRequest(
            validate_only=(
                settings.openai_ads_validate_only
                if validate_only is None
                else validate_only
            ),
            events=events,
        )

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/v1/events",
                params={"pid": self.pixel_id},
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=request.model_dump(exclude_none=True),
            )
            response.raise_for_status()
            return response.json()

    async def send_order_created(
        self,
        *,
        order_id: str,
        amount_minor: int,
        currency: str | None = None,
        contents: list[OpenAIAdsContent] | None = None,
        timestamp: datetime | None = None,
        oppref: str | None = None,
        source_url: str | None = None,
        user: dict[str, Any] | None = None,
        opt_out: bool = False,
        validate_only: bool | None = None,
    ) -> dict[str, Any]:
        """Send an order_created event using a stable order ID for deduplication.

        amount_minor must be the currency's lowest denomination (for RUB,
        kopecks). This prevents accidental decimal/major-unit revenue values.
        """
        if amount_minor < 0:
            raise ValueError("amount_minor не может быть отрицательным")

        event_time = timestamp or datetime.now(timezone.utc)
        self._validate_timestamp(event_time)
        timestamp_ms = int(event_time.timestamp() * 1000)
        event_source_url = source_url or settings.openai_ads_source_url

        event_data: dict[str, Any] = {
            "type": "contents",
            "amount": amount_minor,
            "currency": (currency or settings.openai_ads_default_currency).upper(),
        }
        if contents:
            event_data["contents"] = [item.model_dump(exclude_none=True) for item in contents]

        event = OpenAIAdsEvent(
            id=order_id,
            type="order_created",
            timestamp_ms=timestamp_ms,
            oppref=oppref,
            source_url=event_source_url,
            action_source="web",
            user=user,
            opt_out=opt_out,
            data=event_data,
        )

        if event.action_source == "web" and not event.source_url:
            raise ValueError("source_url обязателен для web-события")

        return await self.send_events([event], validate_only=validate_only)
