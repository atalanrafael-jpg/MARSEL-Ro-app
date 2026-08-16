from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    roapp_base_url: str = "https://api.roapp.io/v2"
    roapp_api_key: str = ""
    roapp_timeout_seconds: float = 30
    roapp_max_requests_per_second: int = 3
    roapp_max_retries: int = 3
    roapp_retry_base_seconds: float = 0.75

    # OpenAI Ads Conversions API credentials must come from Ads Manager > Conversions.
    # Never use the general OpenAI Platform API key for this integration.
    openai_ads_pixel_id: str = ""
    openai_ads_conversions_api_key: str = ""
    openai_ads_base_url: str = "https://bzr.openai.com"
    openai_ads_validate_only: bool = True
    openai_ads_default_currency: str = "RUB"
    openai_ads_source_url: str = ""
    openai_ads_timeout_seconds: float = 15

    # MCP / ChatGPT / Codex integration.
    # HTTP mode is disabled by default so existing deployments remain unchanged.
    # Enable HTTP mode only with a real OAuth 2.1/OIDC issuer and HTTPS resource URL.
    mcp_http_enabled: bool = False
    mcp_resource_server_url: str = ""
    mcp_auth_issuer: str = ""
    mcp_auth_jwks_url: str = ""
    mcp_required_scopes: list[str] = Field(default_factory=list)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
