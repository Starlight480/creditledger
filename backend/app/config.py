"""
Application configuration - loads from environment variables.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "CreditLedger"
    APP_URL: str = "http://localhost:8000"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Security
    SECRET_KEY: str = "change-me-in-production-minimum-32-chars-long"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 43200

    # Database
    DATABASE_URL: str = "sqlite:///./creditledger.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

