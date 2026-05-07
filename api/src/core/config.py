"""Application settings loaded from environment and .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://knowledge:change_me@localhost:5432/knowledge_db"
    redis_host: str = "localhost"
    redis_port: int = 6379
    api_key_rate_limit: int = 1000
    environment: str = "development"
    log_level: str = "INFO"
    sql_echo: bool = False
    # Neo4j
    neo4j_bolt_url: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "change_me_in_production"


settings = Settings()
