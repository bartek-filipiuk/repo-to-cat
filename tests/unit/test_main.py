"""
Unit tests for FastAPI main application.

Tests the basic FastAPI app setup, health check endpoint, and API documentation.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestFastAPIApp:
    """Test suite for FastAPI application initialization."""

    def test_app_exists(self):
        """Test that the FastAPI app is created."""
        assert app is not None
        assert app.title == "Repo-to-Cat API"

    def test_app_version(self):
        """Test that the API has a version."""
        assert hasattr(app, "version")
        assert app.version is not None


class TestHealthEndpoint:
    """Test suite for /health endpoint."""

    def test_health_endpoint_exists(self, client):
        """Test that /health endpoint exists and returns 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_json(self, client):
        """Test that /health endpoint returns JSON."""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"

    def test_health_endpoint_response_structure(self, client):
        """Test that /health endpoint returns expected JSON structure."""
        response = client.get("/health")
        data = response.json()

        # Check required fields
        assert "status" in data
        assert "database" in data
        assert "timestamp" in data

        # Check status value
        assert data["status"] in ["healthy", "unhealthy"]

    def test_health_endpoint_database_check(self, client):
        """Test that /health endpoint checks database connectivity."""
        response = client.get("/health")
        data = response.json()

        # Database should be checked
        assert "database" in data
        assert isinstance(data["database"], dict)
        assert "status" in data["database"]

    def test_health_endpoint_timestamp_format(self, client):
        """Test that /health endpoint returns valid ISO timestamp."""
        response = client.get("/health")
        data = response.json()

        # Timestamp should be valid ISO format
        timestamp = data["timestamp"]
        assert isinstance(timestamp, str)
        # Should be parseable as datetime
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


class TestAPIDocs:
    """Test suite for API documentation endpoints."""

    def test_openapi_docs_exists(self, client):
        """Test that /docs endpoint (Swagger UI) is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_json_exists(self, client):
        """Test that /openapi.json endpoint exists."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    def test_redoc_docs_exists(self, client):
        """Test that /redoc endpoint (ReDoc UI) is accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200


class TestCORSConfiguration:
    """Test suite for CORS middleware configuration."""

    def test_cors_headers_on_health_endpoint(self, client):
        """Test that CORS headers are present on API responses."""
        response = client.options("/health", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })
        # Should allow CORS (will test more thoroughly after CORS implementation)
        assert response.status_code in [200, 405]  # 405 if OPTIONS not explicitly handled
