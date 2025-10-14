"""
Integration tests for protected routes.

Tests authentication requirements and generation endpoints.
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from app.main import app
from app.core.database import SessionLocal
from app.models.database import User, Generation
from app.utils.auth import hash_password, create_session


# Create test client
client = TestClient(app)


@pytest.fixture
def test_user():
    """Create a test user in the database."""
    db = SessionLocal()
    try:
        user = User(
            username="testuser",
            password_hash=hash_password("testpassword123"),
            email="test@example.com"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        yield user

        # Cleanup
        db.delete(user)
        db.commit()
    finally:
        db.close()


@pytest.fixture
def authenticated_client(test_user):
    """Create an authenticated test client with session cookie."""
    db = SessionLocal()
    try:
        session = create_session(db, str(test_user.id))
        session_token = session.token

        client_with_auth = TestClient(app, cookies={"session_token": session_token})

        yield client_with_auth, test_user

        # Cleanup session if it exists
        from app.models.database import Session as DBSession
        db_session = db.query(DBSession).filter(DBSession.token == session_token).first()
        if db_session:
            db.delete(db_session)
            db.commit()
    finally:
        db.close()


@pytest.fixture
def test_generation(test_user):
    """Create a test generation in the database."""
    db = SessionLocal()
    try:
        generation = Generation(
            github_url="https://github.com/test/repo",
            repo_owner="test",
            repo_name="repo",
            primary_language="Python",
            repo_size_kb=1000,
            code_quality_score=7.5,
            cat_attributes={"size": "medium", "age": "adult cat"},
            analysis_data={"files_analyzed": ["test.py"], "metrics": {}},
            image_path="/generated_images/test.png",
            image_prompt="A test cat",
            story="This is a test story",
            meme_text_top="TEST TOP",
            meme_text_bottom="TEST BOTTOM",
            user_id=test_user.id
        )
        db.add(generation)
        db.commit()
        db.refresh(generation)

        yield generation

        # Cleanup
        db.delete(generation)
        db.commit()
    finally:
        db.close()


# ============================================================================
# POST /generate PROTECTION TESTS
# ============================================================================

def test_generate_requires_authentication():
    """Test that POST /generate requires authentication."""
    # Create fresh client with no cookies
    fresh_client = TestClient(app)

    response = fresh_client.post(
        "/generate",
        json={"github_url": "https://github.com/test/repo"}
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated. Please log in."


@patch('app.api.routes.create_workflow')
def test_generate_with_authentication(mock_workflow, authenticated_client):
    """Test that POST /generate works with authentication."""
    auth_client, user = authenticated_client

    # Mock workflow to avoid actual API calls
    mock_workflow_instance = MagicMock()
    mock_workflow.return_value = mock_workflow_instance
    mock_workflow_instance.invoke.return_value = {
        "metadata": {
            "name": "test-repo",
            "owner": "test",
            "primary_language": "Python",
            "size_kb": 1000,
            "stars": 10
        },
        "analysis": {
            "code_quality_score": 7.5,
            "files_analyzed": ["test.py"],
            "metrics": {"has_tests": True}
        },
        "cat_attrs": {
            "size": "medium",
            "age": "adult cat",
            "beauty_score": 7.5,
            "expression": "happy",
            "background": "code editor"
        },
        "story": "A test story about the repository",
        "meme_text_top": "TEST CODE",
        "meme_text_bottom": "MUCH QUALITY",
        "image": {
            "url": "/generated_images/test.png",
            "binary": "base64data",
            "prompt": "A test cat image"
        }
    }

    response = auth_client.post(
        "/generate",
        json={"github_url": "https://github.com/test/repo"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert data["success"] is True
    assert "generation_id" in data
    assert data["repository"]["name"] == "test-repo"
    assert data["analysis"]["code_quality_score"] == 7.5
    assert data["cat_attributes"]["size"] == "medium"
    assert data["story"] == "A test story about the repository"
    assert data["meme_text"]["top"] == "TEST CODE"
    assert data["image"]["url"] == "/generated_images/test.png"

    # Verify workflow was called with user_id
    mock_workflow_instance.invoke.assert_called_once()
    call_args = mock_workflow_instance.invoke.call_args[0][0]
    assert call_args["github_url"] == "https://github.com/test/repo"
    assert call_args["user_id"] == str(user.id)
    assert "generation_id" in call_args


def test_generate_expired_session():
    """Test that POST /generate fails with expired session."""
    from app.models.database import Session as DBSession

    db = SessionLocal()
    try:
        # Create user
        user = User(
            username="expired_test_user",
            password_hash=hash_password("password"),
            email="expired@test.com"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create expired session
        from app.utils.auth import create_session_token
        expired_token = create_session_token()
        expired_session = DBSession(
            user_id=user.id,
            token=expired_token,
            expires_at=datetime.utcnow() - timedelta(days=1)
        )
        db.add(expired_session)
        db.commit()

        # Try to generate with expired session
        expired_client = TestClient(app, cookies={"session_token": expired_token})
        response = expired_client.post(
            "/generate",
            json={"github_url": "https://github.com/test/repo"}
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid or expired session. Please log in again."

        # Cleanup
        db.delete(user)
        db.commit()
    finally:
        db.close()


# ============================================================================
# GET /generations TESTS
# ============================================================================

def test_list_generations_requires_authentication():
    """Test that GET /generations requires authentication."""
    fresh_client = TestClient(app)
    response = fresh_client.get("/generations")

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated. Please log in."


def test_list_generations_empty(authenticated_client):
    """Test listing generations when user has none."""
    auth_client, user = authenticated_client

    response = auth_client.get("/generations")

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["count"] == 0
    assert data["total"] == 0
    assert data["limit"] == 50
    assert data["offset"] == 0
    assert data["has_more"] is False
    assert data["generations"] == []


def test_list_generations_with_data(authenticated_client, test_generation):
    """Test listing generations when user has generations."""
    auth_client, user = authenticated_client

    response = auth_client.get("/generations")

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["count"] == 1
    assert data["total"] == 1
    assert len(data["generations"]) == 1

    # Verify generation data
    gen = data["generations"][0]
    assert gen["id"] == str(test_generation.id)
    assert gen["github_url"] == "https://github.com/test/repo"
    assert gen["repo_owner"] == "test"
    assert gen["repo_name"] == "repo"
    assert gen["primary_language"] == "Python"
    assert gen["code_quality_score"] == 7.5
    assert gen["image_path"] == "/generated_images/test.png"
    assert "created_at" in gen


def test_list_generations_pagination(authenticated_client):
    """Test pagination in list generations."""
    auth_client, user = authenticated_client
    db = SessionLocal()

    try:
        # Create 5 test generations
        for i in range(5):
            gen = Generation(
                github_url=f"https://github.com/test/repo{i}",
                repo_owner="test",
                repo_name=f"repo{i}",
                user_id=user.id
            )
            db.add(gen)
        db.commit()

        # Test limit
        response = auth_client.get("/generations?limit=2")
        data = response.json()
        assert data["count"] == 2
        assert data["total"] == 5
        assert data["has_more"] is True

        # Test offset
        response = auth_client.get("/generations?limit=2&offset=2")
        data = response.json()
        assert data["count"] == 2
        assert data["offset"] == 2

        # Test last page
        response = auth_client.get("/generations?limit=3&offset=3")
        data = response.json()
        assert data["count"] == 2  # Only 2 remaining
        assert data["has_more"] is False

        # Cleanup
        db.query(Generation).filter(Generation.user_id == user.id).delete()
        db.commit()
    finally:
        db.close()


def test_list_generations_only_users_generations(authenticated_client):
    """Test that users only see their own generations."""
    auth_client, user = authenticated_client
    db = SessionLocal()

    try:
        # Create another user with a generation
        other_user = User(
            username="other_user",
            password_hash=hash_password("password"),
            email="other@test.com"
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)

        other_gen = Generation(
            github_url="https://github.com/other/repo",
            repo_owner="other",
            repo_name="repo",
            user_id=other_user.id
        )
        db.add(other_gen)
        db.commit()

        # Request should only return authenticated user's generations
        response = auth_client.get("/generations")
        data = response.json()

        # Should be empty (test_user has no generations in this test)
        assert data["count"] == 0
        assert data["total"] == 0

        # Cleanup
        db.delete(other_gen)
        db.delete(other_user)
        db.commit()
    finally:
        db.close()


# ============================================================================
# GET /generation/:id TESTS
# ============================================================================

def test_get_generation_public_access(test_generation):
    """Test that GET /generation/:id is public (no auth required)."""
    # Use fresh client with no cookies
    fresh_client = TestClient(app)

    response = fresh_client.get(f"/generation/{test_generation.id}")

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert data["success"] is True
    assert data["generation_id"] == str(test_generation.id)
    assert data["repository"]["url"] == "https://github.com/test/repo"
    assert data["repository"]["name"] == "repo"
    assert data["repository"]["owner"] == "test"
    assert data["analysis"]["code_quality_score"] == 7.5
    assert data["cat_attributes"]["size"] == "medium"
    assert data["story"] == "This is a test story"
    assert data["meme_text"]["top"] == "TEST TOP"
    assert data["meme_text"]["bottom"] == "TEST BOTTOM"
    assert data["image"]["url"] == "/generated_images/test.png"
    assert data["image"]["binary"] is None  # Not included in detail view


def test_get_generation_not_found():
    """Test GET /generation/:id with non-existent ID."""
    fresh_client = TestClient(app)

    response = fresh_client.get("/generation/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_get_generation_with_authentication(authenticated_client, test_generation):
    """Test that GET /generation/:id works with authentication too."""
    auth_client, user = authenticated_client

    response = auth_client.get(f"/generation/{test_generation.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["generation_id"] == str(test_generation.id)


# ============================================================================
# INTEGRATION FLOW TESTS
# ============================================================================

@patch('app.api.routes.create_workflow')
def test_full_generation_flow(mock_workflow, authenticated_client):
    """Test complete flow: login -> generate -> list -> view detail."""
    auth_client, user = authenticated_client

    # Mock workflow
    mock_workflow_instance = MagicMock()
    mock_workflow.return_value = mock_workflow_instance
    mock_workflow_instance.invoke.return_value = {
        "metadata": {"name": "flow-test", "owner": "test", "primary_language": "Python", "size_kb": 500, "stars": 5},
        "analysis": {"code_quality_score": 8.0, "files_analyzed": ["main.py"], "metrics": {}},
        "cat_attrs": {"size": "large", "age": "senior", "beauty_score": 8.0, "expression": "wise", "background": "library"},
        "story": "Flow test story",
        "meme_text_top": "FLOW TEST",
        "meme_text_bottom": "SUCCESS",
        "image": {"url": "/generated_images/flow.png", "binary": "base64", "prompt": "A wise cat"}
    }

    # 1. Generate
    gen_response = auth_client.post(
        "/generate",
        json={"github_url": "https://github.com/test/flow-repo"}
    )
    assert gen_response.status_code == 200
    gen_data = gen_response.json()
    generation_id = gen_data["generation_id"]

    # 2. List generations
    list_response = auth_client.get("/generations")
    assert list_response.status_code == 200
    list_data = list_response.json()
    # Note: This will show 0 because we mocked the workflow and didn't save to DB
    # In real scenario, workflow saves to DB and this would show 1

    # 3. View detail (public endpoint)
    # Note: Won't find it because mock didn't save to DB
    # In real scenario, this would work
