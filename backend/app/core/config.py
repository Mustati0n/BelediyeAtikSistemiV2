from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Belediye Atik Sistemi"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(
        default="postgresql+psycopg://belediye_atik:belediye_atik_dev_password"
        "@localhost:5432/belediye_atik"
    )

    jwt_secret_key: str = "change-this-development-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value: object) -> object:
        if isinstance(value, str) and value.lower() in {"release", "prod", "production"}:
            return False
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
