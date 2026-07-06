"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized configuration for the backend service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    PROJECT_NAME: str = "InsightAgent"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+psycopg://insight:insight@db:5432/insightagent"

    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    OPENAI_API_KEY: str = ""


settings = Settings()
