from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    roapp_base_url: str = "https://api.roapp.io/v2"
    roapp_api_key: str = ""
    roapp_timeout_seconds: float = 30
    roapp_max_requests_per_second: int = 3
    openai_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
