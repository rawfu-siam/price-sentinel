"""Configuration management module utilizing Pydantic Settings.

Enforces zero-trust environment security by validating required environment
variables at application startup and loading keys securely.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate project root directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings and runtime guardrails with validation."""

    app_name: str = "Price Sentinel"
    log_level: str = "INFO"
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    target_url: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Instantiate singleton settings object to validate on startup
settings = Settings()
