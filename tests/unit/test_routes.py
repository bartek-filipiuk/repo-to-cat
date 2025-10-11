"""
Unit tests for API routes.

Tests for /health and /generate endpoints with mocked external dependencies.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime
import uuid

from app.main import app


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


# ============================================================================
# HEALTH CHECK HELPER FUNCTION TESTS
# ============================================================================

class TestHealthCheckHelpers:
    """Tests for health check helper functions."""

    def test_check_github_api_success(self):
        """Test GitHub API check when service is up."""
        with patch('httpx.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            from app.api.routes import check_github_api
            result = check_github_api()

            assert result["status"] == "up"
            assert "response_time_ms" in result

    def test_check_github_api_unauthorized(self):
        """Test GitHub API check with 401 (still considered up)."""
        with patch('httpx.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_get.return_value = mock_response

            from app.api.routes import check_github_api
            result = check_github_api()

            assert result["status"] == "up"  # 401 means API is up, just auth issue

    def test_check_github_api_failure(self):
        """Test GitHub API check when service is down."""
        with patch('httpx.get') as mock_get:
            mock_get.side_effect = Exception("Connection timeout")

            from app.api.routes import check_github_api
            result = check_github_api()

            assert result["status"] == "down"
            assert "error" in result

    def test_check_openrouter_api_success(self):
        """Test OpenRouter API check when service is up."""
        with patch('httpx.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            from app.api.routes import check_openrouter_api
            result = check_openrouter_api()

            assert result["status"] == "up"
            assert "response_time_ms" in result

    def test_check_together_api_success(self):
        """Test Together.ai API check when service is up."""
        with patch('httpx.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            from app.api.routes import check_together_api
            result = check_together_api()

            assert result["status"] == "up"
            assert "response_time_ms" in result


# ============================================================================
# HEALTH CHECK ENDPOINT TESTS
# ============================================================================

class TestHealthCheckEndpoint:
    """Tests for GET /health endpoint."""

    def test_health_check_all_services_up(self, client):
        """Test health check when all services are healthy."""
        with patch('app.api.routes.check_github_api') as mock_github, \
             patch('app.api.routes.check_openrouter_api') as mock_openrouter, \
             patch('app.api.routes.check_together_api') as mock_together, \
             patch('sqlalchemy.orm.Session.execute') as mock_execute:

            # Mock all services as healthy
            mock_github.return_value = {"status": "up", "response_time_ms": 150}
            mock_openrouter.return_value = {"status": "up", "response_time_ms": 200}
            mock_together.return_value = {"status": "up", "response_time_ms": 180}
            mock_execute.return_value = None  # Database query succeeds

            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "healthy"
            assert data["services"]["github_api"]["status"] == "up"
            assert data["services"]["openrouter"]["status"] == "up"
            assert data["services"]["together_ai"]["status"] == "up"
            assert data["services"]["database"]["status"] == "up"
            assert "response_time_ms" in data["services"]["github_api"]

    def test_health_check_github_api_down(self, client):
        """Test health check when GitHub API is down."""
        with patch('app.api.routes.check_github_api') as mock_github, \
             patch('app.api.routes.check_openrouter_api') as mock_openrouter, \
             patch('app.api.routes.check_together_api') as mock_together:

            mock_github.return_value = {"status": "down", "error": "Connection timeout"}
            mock_openrouter.return_value = {"status": "up", "response_time_ms": 200}
            mock_together.return_value = {"status": "up", "response_time_ms": 180}

            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "degraded"
            assert data["services"]["github_api"]["status"] == "down"
            assert "error" in data["services"]["github_api"]

    def test_health_check_multiple_services_down(self, client):
        """Test health check when multiple services are down."""
        with patch('app.api.routes.check_github_api') as mock_github, \
             patch('app.api.routes.check_openrouter_api') as mock_openrouter, \
             patch('app.api.routes.check_together_api') as mock_together:

            mock_github.return_value = {"status": "down", "error": "Connection error"}
            mock_openrouter.return_value = {"status": "down", "error": "Timeout"}
            mock_together.return_value = {"status": "up", "response_time_ms": 180}

            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "degraded"
            assert data["services"]["github_api"]["status"] == "down"
            assert data["services"]["openrouter"]["status"] == "down"

    def test_health_check_database_down(self, client):
        """Test health check when database is down."""
        with patch('app.api.routes.check_github_api') as mock_github, \
             patch('app.api.routes.check_openrouter_api') as mock_openrouter, \
             patch('app.api.routes.check_together_api') as mock_together, \
             patch('app.core.database.get_db') as mock_db:

            mock_github.return_value = {"status": "up", "response_time_ms": 150}
            mock_openrouter.return_value = {"status": "up", "response_time_ms": 200}
            mock_together.return_value = {"status": "up", "response_time_ms": 180}

            # Mock database failure
            mock_session = MagicMock()
            mock_session.execute.side_effect = Exception("Database connection failed")
            mock_db.return_value = mock_session

            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "degraded"
            assert data["services"]["database"]["status"] == "down"


# ============================================================================
# GENERATE ENDPOINT TESTS
# ============================================================================

class TestGenerateEndpoint:
    """Tests for POST /generate endpoint."""

    def test_generate_success(self, client):
        """Test successful repository analysis and image generation."""
        with patch('app.api.routes.create_workflow') as mock_workflow:
            # Mock successful workflow execution
            mock_workflow_instance = MagicMock()
            test_generation_id = "test-uuid-123"
            mock_workflow_instance.invoke.return_value = {
                "github_url": "https://github.com/python/cpython",
                "generation_id": test_generation_id,
                "metadata": {
                    "name": "cpython",
                    "owner": "python",
                    "primary_language": "Python",
                    "size_kb": 150000,
                    "stars": 50000
                },
                "analysis": {
                    "code_quality_score": 8.5,
                    "files_analyzed": ["main.py", "tests/test_main.py"],
                    "metrics": {
                        "maintainability": 9.0,
                        "complexity": 8.0
                    }
                },
                "cat_attrs": {
                    "size": "large",
                    "age": "wise old cat",
                    "beauty_score": 8.5,
                    "expression": "confident",
                    "background": "snakes and code snippets"
                },
                "image": {
                    "url": "/generated_images/test-uuid-123.png",
                    "binary": "fake-base64-data",
                    "prompt": "A large, wise old cat..."
                },
                "error": None
            }
            mock_workflow.return_value = mock_workflow_instance

            response = client.post(
                "/generate",
                json={"github_url": "https://github.com/python/cpython"}
            )

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert "generation_id" in data
            assert data["repository"]["name"] == "cpython"
            assert data["repository"]["owner"] == "python"
            assert data["analysis"]["code_quality_score"] == 8.5
            assert data["cat_attributes"]["size"] == "large"
            assert "image" in data
            assert data["image"]["url"] == "/generated_images/test-uuid-123.png"

    def test_generate_invalid_url(self, client):
        """Test generate with invalid GitHub URL."""
        response = client.post(
            "/generate",
            json={"github_url": "https://gitlab.com/some/repo"}
        )

        assert response.status_code == 422
        assert "GitHub repository" in response.text

    def test_generate_empty_url(self, client):
        """Test generate with empty URL."""
        response = client.post(
            "/generate",
            json={"github_url": ""}
        )

        assert response.status_code == 422

    def test_generate_malformed_url(self, client):
        """Test generate with malformed GitHub URL."""
        response = client.post(
            "/generate",
            json={"github_url": "https://github.com/owner"}
        )

        assert response.status_code == 422

    def test_generate_repository_not_found(self, client):
        """Test generate with non-existent repository (404)."""
        with patch('app.api.routes.create_workflow') as mock_workflow:
            mock_workflow_instance = MagicMock()
            mock_workflow_instance.invoke.return_value = {
                "github_url": "https://github.com/nonexistent/repo",
                "generation_id": "test-uuid-456",
                "error": "Repository not found: 404"
            }
            mock_workflow.return_value = mock_workflow_instance

            response = client.post(
                "/generate",
                json={"github_url": "https://github.com/nonexistent/repo"}
            )

            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "not found" in data["detail"].lower()

    def test_generate_private_repository(self, client):
        """Test generate with private repository (403)."""
        with patch('app.api.routes.create_workflow') as mock_workflow:
            mock_workflow_instance = MagicMock()
            mock_workflow_instance.invoke.return_value = {
                "github_url": "https://github.com/private/repo",
                "generation_id": "test-uuid-789",
                "error": "Access forbidden: 403"
            }
            mock_workflow.return_value = mock_workflow_instance

            response = client.post(
                "/generate",
                json={"github_url": "https://github.com/private/repo"}
            )

            assert response.status_code == 403
            data = response.json()
            assert "detail" in data
            assert "forbidden" in data["detail"].lower() or "access" in data["detail"].lower()

    def test_generate_analysis_failure(self, client):
        """Test generate when analysis fails (500)."""
        with patch('app.api.routes.create_workflow') as mock_workflow:
            mock_workflow_instance = MagicMock()
            mock_workflow_instance.invoke.return_value = {
                "github_url": "https://github.com/owner/repo",
                "generation_id": "test-uuid-999",
                "error": "Analysis failed: LLM service unavailable"
            }
            mock_workflow.return_value = mock_workflow_instance

            response = client.post(
                "/generate",
                json={"github_url": "https://github.com/owner/repo"}
            )

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data

    def test_generate_workflow_exception(self, client):
        """Test generate when workflow raises exception."""
        with patch('app.api.routes.create_workflow') as mock_workflow:
            mock_workflow_instance = MagicMock()
            mock_workflow_instance.invoke.side_effect = Exception("Unexpected error")
            mock_workflow.return_value = mock_workflow_instance

            response = client.post(
                "/generate",
                json={"github_url": "https://github.com/owner/repo"}
            )

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "error" in data["detail"].lower()


# ============================================================================
# STATIC FILE SERVING TESTS
# ============================================================================

class TestStaticFileServing:
    """Tests for static file serving of generated images."""

    def test_static_files_mounted(self, client):
        """Test that static files endpoint is properly mounted."""
        # The static files mount should return 404 for non-existent files
        response = client.get("/generated_images/nonexistent.png")
        assert response.status_code == 404

    def test_root_endpoint_includes_generate(self, client):
        """Test that root endpoint includes generate in response."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "generate" in data
        assert data["generate"] == "/generate"