from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application configuration using Pydantic settings."""

    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_service_key: str

    # LLM Providers (for internal use)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # API
    aperture_api_key: str
    environment: str = "development"

    # Short Links
    short_link_domain: str = "localhost:8000"

    # Assessment
    default_assessment_model: str = "gpt-4o-mini"
    assessment_temperature: float = 0.3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
