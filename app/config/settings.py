from enum import Enum
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Environment enum."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Settings class."""

    app_name: str = "HoverHub"
    environment: Environment = Environment.DEVELOPMENT
    host: str = "0.0.0.0"
    port: int = 8000
    db_connection_string: str
    cache_connection_string: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    """Get the settings."""
    return Settings()
