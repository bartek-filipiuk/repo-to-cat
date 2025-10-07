"""
Application configuration settings.

Uses pydantic-settings to load from environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # GitHub Configuration
    GITHUB_TOKEN: str

    # AI Provider Keys
    OPENROUTER_API_KEY: str
    TOGETHER_API_KEY: str

    # Database Configuration
    DATABASE_URL: str

    # Application Settings (with defaults)
    IMAGE_STORAGE_PATH: str = "./generated_images"
    API_PORT: int = 8000
    ENV: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


# Global settings instance
settings = Settings()
