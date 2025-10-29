"""Application configuration and dependency wiring."""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

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
    twilio_account_sid: Optional[str] = Field(default=None, description="Twilio account SID")
    twilio_auth_token: Optional[str] = Field(default=None, description="Twilio auth token")
    twilio_base_url: AnyHttpUrl | None = Field(
        default="https://api.twilio.com/2010-04-01", description="Twilio REST API base URL"
    )
    zendesk_subdomain: Optional[str] = Field(default=None)
    zendesk_email: Optional[str] = Field(default=None)
    zendesk_api_token: Optional[str] = Field(default=None)
    salesforce_instance_url: Optional[AnyHttpUrl] = Field(default=None)
    salesforce_client_id: Optional[str] = Field(default=None)
    salesforce_client_secret: Optional[str] = Field(default=None)
    salesforce_refresh_token: Optional[str] = Field(default=None)
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

