"""Application settings loaded from environment and .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://knowledge:change_me@localhost:5432/knowledge_db"
    environment: str = "development"
    log_level: str = "INFO"
    sql_echo: bool = False


settings = Settings()
