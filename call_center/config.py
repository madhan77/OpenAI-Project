"""Application configuration and dependency wiring."""
from __future__ import annotations

from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Strongly-typed configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_prefix="CALL_CENTER_", env_file=".env", extra="ignore")

    environment: str = Field(default="development", description="Deployment environment name")
    database_url: str = Field(
        default="sqlite+aiosqlite:///./call_center.db",
        description="SQLAlchemy connection string for the operational data store.",
    )
    signing_key: str = Field(
        default="dev-secret-key",
        description="Symmetric key used for JWT signing in development deployments.",
    )
    prometheus_enabled: bool = Field(
        default=True,
        description="Expose Prometheus metrics endpoint when True.",
    )
    firebase_project_id: str = Field(
        default="call-center-demo",
        description="Firebase project identifier used for authentication",
    )
    firebase_web_api_key: str = Field(
        default="demo-api-key",
        description="Firebase Web API key used by the front-end",
    )
    firebase_emulator_mode: bool = Field(
        default=True,
        description="When True, tokens are verified using the local emulator secret instead of remote JWKS",
    )
    firebase_emulator_jwt_secret: str = Field(
        default="firebase-emulator-secret",
        description="Shared secret used to mint and verify emulator ID tokens",
    )
    firebase_service_account_cert: str | None = Field(
        default=None,
        description="PEM-encoded certificate for verifying Firebase tokens when not using the emulator",
    )
    recording_retention_days: int = Field(
        default=60,
        description="Default recording retention policy in days if queue-specific value not provided.",
    )
    data_residency_region: str = Field(
        default="us",
        description="Primary data residency region. Must be either 'us' or 'eu'.",
        pattern="^(us|eu)$",
    )
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"],
        description="CORS origins allowed for API and websocket traffic.",
    )


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """Return a cached configuration instance."""

    return AppConfig()

