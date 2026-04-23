from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="traceflow")
    env: str = Field(default="local")
    debug: bool = Field(default=False)
    api_v1_prefix: str = Field(default="/api/v1")
    database_url: str = Field(
        default="postgresql+psycopg://traceflow:traceflow@localhost:5432/traceflow"
    )
    log_level: str = Field(default="INFO")
    secret_key: str = Field(default="change-me")
    access_token_expire_minutes: int = Field(default=60)

    model_config = SettingsConfigDict(
        env_prefix="TRACEFLOW_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

