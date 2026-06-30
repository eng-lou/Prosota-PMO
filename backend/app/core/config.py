from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # psycopg3 handles both sync (Alembic) and async (app) with the same URL scheme
    database_url: str = "postgresql+psycopg://postgres:password@localhost:5432/prosotapmo"
    secret_key: str = "change-me-in-production"
    environment: str = "development"
    auth0_domain: str = ""
    auth0_audience: str = ""


settings = Settings()
