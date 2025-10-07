"""
Unit tests for application configuration.

Following TDD: Write tests FIRST, then implement app/core/config.py
"""
import pytest
from pydantic import ValidationError


def test_config_loads_from_env(monkeypatch):
    """Test that Settings can load from environment variables."""
    monkeypatch.setenv("GITHUB_TOKEN", "test_github_token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_openrouter_key")
    monkeypatch.setenv("TOGETHER_API_KEY", "test_together_key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")

    from app.core.config import Settings
    settings = Settings()

    assert settings.GITHUB_TOKEN == "test_github_token"
    assert settings.OPENROUTER_API_KEY == "test_openrouter_key"
    assert settings.TOGETHER_API_KEY == "test_together_key"
    assert settings.DATABASE_URL == "postgresql://test:test@localhost/test"


def test_config_has_default_values(monkeypatch):
    """Test that Settings has sensible defaults for optional fields."""
    # Set required env vars
    monkeypatch.setenv("GITHUB_TOKEN", "test_token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
    monkeypatch.setenv("TOGETHER_API_KEY", "test_key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")

    from app.core.config import Settings
    settings = Settings()

    # Check defaults
    assert settings.IMAGE_STORAGE_PATH == "./generated_images"
    assert settings.API_PORT == 8000
    assert settings.ENV == "development"


def test_config_raises_error_if_missing_required_fields():
    """Test that Settings raises ValidationError when required env vars are missing."""
    with pytest.raises(ValidationError) as exc_info:
        from app.core.config import Settings
        Settings()

    # Verify error mentions missing fields
    error_msg = str(exc_info.value)
    assert "GITHUB_TOKEN" in error_msg or "Field required" in error_msg


def test_config_allows_override_of_defaults(monkeypatch):
    """Test that default values can be overridden via environment variables."""
    monkeypatch.setenv("GITHUB_TOKEN", "test_token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
    monkeypatch.setenv("TOGETHER_API_KEY", "test_key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")
    monkeypatch.setenv("IMAGE_STORAGE_PATH", "/custom/path")
    monkeypatch.setenv("API_PORT", "9000")
    monkeypatch.setenv("ENV", "production")

    from app.core.config import Settings
    settings = Settings()

    assert settings.IMAGE_STORAGE_PATH == "/custom/path"
    assert settings.API_PORT == 9000
    assert settings.ENV == "production"
