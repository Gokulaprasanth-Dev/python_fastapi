from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """

    # Application metadata
    app_name: str
    app_version: str

    # Runtime environment
    environment: Literal["local", "dev", "staging", "prod"] = "local"
    debug: bool = False

    # PostgreSQL
    database_url: str

    # JWT
    jwt_secret_key: SecretStr = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=60, gt=0)

    # AWS S3
    aws_access_key_id: SecretStr | None = None
    aws_secret_access_key: SecretStr | None = None
    aws_region: str
    aws_s3_bucket_name: str
    aws_endpoint_url: str | None = None

    # CORS
    cors_allowed_origins: list[str] = Field(default_factory=list)

    # Trusted hosts
    trusted_hosts: list[str] = Field(default_factory=list)

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        frozen=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
