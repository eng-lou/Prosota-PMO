from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/prosotapmo"
    sync_database_url: str = "postgresql+psycopg2://postgres:password@localhost:5432/prosotapmo"
    secret_key: str = "change-me-in-production"
    environment: str = "development"


settings = Settings()
