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
    openai_ads_validate_only: bool = False
    openai_ads_default_currency: str = "RUB"
    openai_ads_source_url: str = ""
    openai_ads_timeout_seconds: float = 15

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
