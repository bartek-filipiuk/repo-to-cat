"""
Pytest configuration and shared fixtures.

IMPORTANT: This file sets environment variables at module import time,
BEFORE any other imports, to prevent ValidationError from Settings().
"""
import os

# ============================================================================
# CRITICAL: Set environment variables BEFORE any app imports
# ============================================================================
# This must happen at module level (not in a fixture) because pytest
# imports test modules before running fixtures. If Settings() is instantiated
# during import (via app.main), it will fail validation in CI environments
# without these variables.

# Set default test values if not already set (allows real .env to override)
if "GITHUB_TOKEN" not in os.environ:
    os.environ["GITHUB_TOKEN"] = "test_github_token_123"

if "OPENROUTER_API_KEY" not in os.environ:
    os.environ["OPENROUTER_API_KEY"] = "test_openrouter_key_456"

if "TOGETHER_API_KEY" not in os.environ:
    os.environ["TOGETHER_API_KEY"] = "test_together_key_789"

if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "postgresql://repo_user:repo_password@localhost:5434/repo_to_cat"


# ============================================================================
# Now it's safe to import pytest and define fixtures
# ============================================================================
import pytest


@pytest.fixture
def test_env_vars():
    """
    Fixture that provides access to test environment variables.

    Useful if tests need to verify or modify env vars during test execution.
    """
    return {
        "GITHUB_TOKEN": os.environ["GITHUB_TOKEN"],
        "OPENROUTER_API_KEY": os.environ["OPENROUTER_API_KEY"],
        "TOGETHER_API_KEY": os.environ["TOGETHER_API_KEY"],
        "DATABASE_URL": os.environ["DATABASE_URL"],
    }
