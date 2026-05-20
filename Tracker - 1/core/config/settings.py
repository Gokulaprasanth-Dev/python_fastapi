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

    # JWT authentication configuration
    jwt_secret_key: SecretStr = Field(
        min_length=32
    )

    jwt_algorithm: str = "HS256"

    jwt_access_token_expire_minutes: int = Field(
        default=60,
        gt=0,
    )

    # AWS S3 configuration
    aws_access_key_id: SecretStr | None = None
    aws_secret_access_key: SecretStr | None = None

    aws_region: str
    aws_s3_bucket_name: str

    # Pydantic settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",   # Load environment variables from .env
        extra="ignore",   # Ignore unknown environment variables
        frozen=True,      # Make settings immutable after initialization
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached application settings instance.

    Using lru_cache ensures:
    - environment variables are loaded only once
    - settings object is reused across the application
    - improved performance and consistency

    Returns:
        Application settings instance.
    """

    return Settings()