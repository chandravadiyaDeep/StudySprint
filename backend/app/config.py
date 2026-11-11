"""Environment-backed application settings."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Secrets are read only from the server environment, never from frontend code.
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    cors_origins: str = "http://localhost:5500,http://127.0.0.1:5500"
    max_papers_per_request: int = 10
    max_chars_per_paper: int = 120_000
    max_total_chars: int = 500_000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        # Parse a comma-separated list without accepting wildcard origins by default.
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
