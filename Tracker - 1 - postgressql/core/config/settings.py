from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.

    Values are automatically validated and parsed by Pydantic.
    """

    # Application metadata
    app_name: str
    app_version: str

    # Runtime environment
    environment: Literal["local", "dev", "staging", "prod"] = "local"
    debug: bool = False

    # MongoDB
    mongo_uri: str
    mongo_db: str
    # Set False when running against a standalone mongod (no replica set).
    # Never False in staging/prod.
    mongo_transactions_enabled: bool = True

    # JWT
    jwt_secret_key: SecretStr = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=60, gt=0)

    # AWS S3 — both may be None when using instance-profile / IAM-role auth
    aws_access_key_id: SecretStr | None = None
    aws_secret_access_key: SecretStr | None = None
    aws_region: str
    aws_s3_bucket_name: str
    aws_endpoint_url: str | None = None

    # CORS — comma-separated allowed origins, e.g. "https://app.example.com,https://admin.example.com"
    # Leave empty to deny all cross-origin requests (recommended for production APIs).
    cors_allowed_origins: list[str] = Field(default_factory=list)

    # Trusted hosts — leave empty to allow all (only for local dev)
    trusted_hosts: list[str] = Field(default_factory=list)

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        frozen=True,
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached application settings instance.

    Using lru_cache ensures environment variables are loaded only once
    and the settings object is reused across the application.
    """
    return Settings()
