"""Application configuration."""
from functools import lru_cache
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

    # Database
    database_url: str = "postgresql+asyncpg://harvester:harvester@db:5432/harvester"

    # JWT
    jwt_secret_key: str = "change-me-in-production-use-env"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # Security
    bcrypt_rounds: int = 12

    # Admin: при регистрации с этим email пользователь получает роль Admin
    initial_admin_email: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
