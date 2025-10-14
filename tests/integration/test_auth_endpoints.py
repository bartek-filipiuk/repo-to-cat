"""
Integration tests for authentication endpoints.

Tests login, logout, and user session management via API.
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.database import User, Session as DBSession
from app.utils.auth import hash_password, create_session_token, create_session


# Create test client
client = TestClient(app)


@pytest.fixture
def test_user():
    """
    Fixture to create a test user in the database.

    Yields the user, then cleans up after the test.
    """
    db = SessionLocal()
    try:
        # Create test user
        user = User(
            username="testuser",
            password_hash=hash_password("testpassword123"),
            email="test@example.com"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        yield user

        # Cleanup: delete user (cascade deletes sessions)
        db.delete(user)
        db.commit()
    finally:
        db.close()


@pytest.fixture
def authenticated_client(test_user):
    """
    Fixture to create an authenticated test client with session cookie.

    Yields (client, user, session_token).
    """
    db = SessionLocal()
    try:
        # Create session for test user
        session = create_session(db, str(test_user.id))
        session_token = session.token

        # Create client with session cookie
        client_with_auth = TestClient(app, cookies={"session_token": session_token})

        yield client_with_auth, test_user, session_token

        # Cleanup: delete session if it still exists
        db_session = db.query(DBSession).filter(DBSession.token == session_token).first()
        if db_session:
            db.delete(db_session)
            db.commit()
    finally:
        db.close()


# ============================================================================
# LOGIN TESTS
# ============================================================================

def test_login_success(test_user):
    """Test successful login with valid credentials."""
    response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "testpassword123"
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert data["success"] is True
    assert data["message"] == "Login successful"
    assert data["user"]["username"] == "testuser"
    assert data["user"]["email"] == "test@example.com"
    assert "id" in data["user"]
    assert "created_at" in data["user"]

    # Verify session cookie was set
    assert "session_token" in response.cookies
    session_token = response.cookies["session_token"]
    assert len(session_token) == 64  # 64-char hex token

    # Verify cookie properties (httponly, samesite)
    # Note: TestClient doesn't expose all cookie properties directly,
    # but we can verify the token exists and has correct length


def test_login_invalid_username():
    """Test login with non-existent username."""
    response = client.post(
        "/auth/login",
        json={
            "username": "nonexistent_user",
            "password": "somepassword"
        }
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid username or password"

    # Verify no session cookie was set
    assert "session_token" not in response.cookies


def test_login_invalid_password(test_user):
    """Test login with wrong password."""
    response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "wrong_password"
        }
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid username or password"

    # Verify no session cookie was set
    assert "session_token" not in response.cookies


def test_login_empty_credentials():
    """Test login with empty username/password."""
    # Empty username
    response = client.post(
        "/auth/login",
        json={
            "username": "",
            "password": "password"
        }
    )
    assert response.status_code == 422  # Validation error

    # Empty password
    response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": ""
        }
    )
    assert response.status_code == 422  # Validation error


def test_login_missing_fields():
    """Test login with missing fields."""
    # Missing password
    response = client.post(
        "/auth/login",
        json={"username": "testuser"}
    )
    assert response.status_code == 422  # Validation error

    # Missing username
    response = client.post(
        "/auth/login",
        json={"password": "password"}
    )
    assert response.status_code == 422  # Validation error


# ============================================================================
# LOGOUT TESTS
# ============================================================================

def test_logout_authenticated(authenticated_client):
    """Test logout when authenticated."""
    auth_client, user, session_token = authenticated_client

    response = auth_client.post("/auth/logout")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Logged out successfully"

    # Verify session was deleted from database
    db = SessionLocal()
    try:
        session = db.query(DBSession).filter(DBSession.token == session_token).first()
        assert session is None
    finally:
        db.close()


def test_logout_not_authenticated():
    """Test logout when not authenticated (no session cookie)."""
    # Create a fresh client with no cookies
    fresh_client = TestClient(app)
    response = fresh_client.post("/auth/logout")

    # Logout without session token should return 200 (idempotent operation)
    # This is the actual behavior and is reasonable - logout always succeeds
    # even if you weren't logged in
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Logged out successfully"


def test_logout_invalid_session():
    """Test logout with invalid session token."""
    # Create client with fake session token
    fake_client = TestClient(app, cookies={"session_token": "fake_token_123"})

    response = fake_client.post("/auth/logout")

    # Should still return 200 (cookie cleared even if session not found)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Logged out successfully"


# ============================================================================
# GET /auth/me TESTS
# ============================================================================

def test_get_me_authenticated(authenticated_client):
    """Test GET /auth/me when authenticated."""
    auth_client, user, session_token = authenticated_client

    response = auth_client.get("/auth/me")

    assert response.status_code == 200
    data = response.json()

    # Verify user data
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data

    # Verify no sensitive fields
    assert "password_hash" not in data
    assert "api_token" not in data


def test_get_me_not_authenticated():
    """Test GET /auth/me when not authenticated."""
    # Create fresh client with no cookies
    fresh_client = TestClient(app)
    response = fresh_client.get("/auth/me")

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated. Please log in."


def test_get_me_expired_session(test_user):
    """Test GET /auth/me with expired session."""
    db = SessionLocal()
    try:
        # Create expired session
        expired_token = create_session_token()
        expired_session = DBSession(
            user_id=test_user.id,
            token=expired_token,
            expires_at=datetime.utcnow() - timedelta(days=1)  # Expired yesterday
        )
        db.add(expired_session)
        db.commit()

        # Try to access /auth/me with expired token
        expired_client = TestClient(app, cookies={"session_token": expired_token})
        response = expired_client.get("/auth/me")

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid or expired session. Please log in again."

        # Verify expired session was deleted
        deleted_session = db.query(DBSession).filter(
            DBSession.token == expired_token
        ).first()
        assert deleted_session is None  # Should be deleted
    finally:
        db.close()


# ============================================================================
# GET /auth/status TESTS
# ============================================================================

def test_auth_status_authenticated(authenticated_client):
    """Test GET /auth/status when authenticated."""
    auth_client, user, session_token = authenticated_client

    response = auth_client.get("/auth/status")

    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is True
    assert data["username"] == "testuser"


def test_auth_status_not_authenticated():
    """Test GET /auth/status when not authenticated."""
    response = client.get("/auth/status")

    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is False
    assert data["username"] is None


# ============================================================================
# SESSION MANAGEMENT TESTS
# ============================================================================

def test_login_creates_session_in_database(test_user):
    """Test that login creates a session in the database."""
    db = SessionLocal()
    try:
        # Login
        response = client.post(
            "/auth/login",
            json={
                "username": "testuser",
                "password": "testpassword123"
            }
        )

        assert response.status_code == 200
        session_token = response.cookies["session_token"]

        # Verify session exists in database
        session = db.query(DBSession).filter(DBSession.token == session_token).first()
        assert session is not None
        assert session.user_id == test_user.id
        assert session.expires_at > datetime.utcnow()
        assert session.expires_at < datetime.utcnow() + timedelta(days=8)

        # Cleanup
        db.delete(session)
        db.commit()
    finally:
        db.close()


def test_multiple_logins_create_multiple_sessions(test_user):
    """Test that multiple logins create separate sessions."""
    db = SessionLocal()
    try:
        # Login twice
        response1 = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "testpassword123"}
        )
        response2 = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "testpassword123"}
        )

        token1 = response1.cookies["session_token"]
        token2 = response2.cookies["session_token"]

        # Tokens should be different
        assert token1 != token2

        # Both sessions should exist
        session1 = db.query(DBSession).filter(DBSession.token == token1).first()
        session2 = db.query(DBSession).filter(DBSession.token == token2).first()
        assert session1 is not None
        assert session2 is not None

        # Cleanup
        db.delete(session1)
        db.delete(session2)
        db.commit()
    finally:
        db.close()


def test_session_token_uniqueness():
    """Test that session tokens are unique."""
    from app.utils.auth import create_session_token

    tokens = [create_session_token() for _ in range(100)]
    assert len(tokens) == len(set(tokens))  # All unique


# ============================================================================
# AUTHENTICATION FLOW TEST
# ============================================================================

def test_full_authentication_flow(test_user):
    """Test complete authentication flow: login -> access protected route -> logout."""
    # 1. Login
    response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpassword123"}
    )
    assert response.status_code == 200
    session_token = response.cookies["session_token"]

    # 2. Access protected route with session
    auth_client = TestClient(app, cookies={"session_token": session_token})
    response = auth_client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

    # 3. Logout
    response = auth_client.post("/auth/logout")
    assert response.status_code == 200

    # 4. Try to access protected route after logout (should fail)
    response = auth_client.get("/auth/me")
    assert response.status_code == 401
