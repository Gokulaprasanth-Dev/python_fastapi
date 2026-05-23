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

    # Runtime environment configuration
    environment: Literal[
        "local",
        "dev",
        "staging",
        "prod",
    ] = "local"

    # Enable or disable debug behavior
    debug: bool = False

    # MongoDB configuration
    mongo_uri: str
    mongo_db: str

    # Fix 3: when False, NoOpUnitOfWork is used so the app can run against a
    # standalone mongod (no replica set) in local dev without crashing on
    # start_transaction(). Never set to False in staging/prod.
    mongo_transactions_enabled: bool = True

    # JWT authentication configuration
    jwt_secret_key: SecretStr = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=60, gt=0)

    # AWS S3 configuration
    aws_access_key_id: SecretStr | None = None
    aws_secret_access_key: SecretStr | None = None
    aws_region: str
    aws_s3_bucket_name: str
    aws_endpoint_url: str | None = None

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
