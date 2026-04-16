"""Application configuration."""
from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "Scientific Data Harvester"
    debug: bool = False
    app_env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # Database
    database_url: str = "postgresql+asyncpg://harvester:harvester@localhost:5433/harvester"

    # JWT
    jwt_secret_key: str = "change-me-in-production-use-env"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # Security
    bcrypt_rounds: int = 12
    cors_origins: str = (
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"
    )

    # Admin: при регистрации с этим email пользователь получает роль Admin
    initial_admin_email: str | None = None

    # Logging
    log_level: str = "INFO"
    log_json: bool = True

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def model_dump_safe(self) -> dict[str, Any]:
        data = self.model_dump()
        if "jwt_secret_key" in data:
            data["jwt_secret_key"] = "***"
        return data


@lru_cache
def get_settings() -> Settings:
    return Settings()
