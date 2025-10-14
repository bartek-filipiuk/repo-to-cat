"""
Unit tests for authentication utilities.

Tests password hashing, session token generation, and session management.
"""
import pytest
from datetime import datetime, timedelta

from app.utils.auth import (
    hash_password,
    verify_password,
    create_session_token,
    create_session,
    verify_session_token,
    delete_session,
    cleanup_expired_sessions
)
from app.core.database import SessionLocal
from app.models.database import User, Session


def test_hash_password():
    """Test that password hashing produces valid bcrypt hash."""
    password = "test_password_123"
    hashed = hash_password(password)

    # Bcrypt hashes are 60 characters
    assert len(hashed) == 60
    # Should start with $2b$ (bcrypt identifier)
    assert hashed.startswith("$2b$")
    # Should not equal the plain password
    assert hashed != password


def test_verify_password_correct():
    """Test password verification with correct password."""
    password = "my_secure_password"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test password verification with incorrect password."""
    password = "correct_password"
    hashed = hash_password(password)

    assert verify_password("wrong_password", hashed) is False


def test_verify_password_invalid_hash():
    """Test password verification with invalid hash format."""
    assert verify_password("password", "not_a_valid_hash") is False


def test_hash_password_different_salts():
    """Test that same password produces different hashes (different salts)."""
    password = "same_password"
    hash1 = hash_password(password)
    hash2 = hash_password(password)

    # Different hashes due to different salts
    assert hash1 != hash2
    # But both should verify correctly
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True


def test_create_session_token():
    """Test session token generation."""
    token = create_session_token()

    # Should be 64 characters (32 bytes as hex)
    assert len(token) == 64
    # Should be hexadecimal
    assert all(c in '0123456789abcdef' for c in token)


def test_create_session_token_uniqueness():
    """Test that generated tokens are unique."""
    tokens = [create_session_token() for _ in range(100)]

    # All tokens should be unique
    assert len(tokens) == len(set(tokens))


def test_create_session():
    """Test creating a session in the database."""
    db = SessionLocal()
    try:
        # Create test user
        test_user = User(
            username="session_test_user",
            password_hash=hash_password("password"),
            email="session@test.com"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        # Create session
        session = create_session(db, test_user.id, expires_in_days=7)

        # Verify session properties
        assert session.id is not None
        assert session.user_id == test_user.id
        assert len(session.token) == 64
        assert session.expires_at > datetime.utcnow()
        assert session.expires_at < datetime.utcnow() + timedelta(days=8)
        assert session.created_at is not None

        # Verify relationship
        assert session.user.username == "session_test_user"

        # Clean up
        db.delete(session)
        db.delete(test_user)
        db.commit()
    finally:
        db.close()


def test_create_session_custom_expiration():
    """Test creating a session with custom expiration."""
    db = SessionLocal()
    try:
        # Create test user
        test_user = User(
            username="session_expiry_test",
            password_hash=hash_password("password"),
            email="expiry@test.com"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        # Create session with 30-day expiration
        session = create_session(db, test_user.id, expires_in_days=30)

        # Verify expiration is approximately 30 days
        expected_expiry = datetime.utcnow() + timedelta(days=30)
        time_diff = abs((session.expires_at - expected_expiry).total_seconds())
        assert time_diff < 5  # Within 5 seconds

        # Clean up
        db.delete(session)
        db.delete(test_user)
        db.commit()
    finally:
        db.close()


def test_create_session_invalid_user():
    """Test creating session with invalid user_id raises error."""
    db = SessionLocal()
    try:
        # Try to create session with non-existent user
        with pytest.raises(ValueError, match="User with id .* not found"):
            create_session(db, "00000000-0000-0000-0000-000000000000")
    finally:
        db.close()


def test_verify_session_token_valid():
    """Test verifying a valid session token."""
    db = SessionLocal()
    try:
        # Create test user and session
        test_user = User(
            username="verify_session_user",
            password_hash=hash_password("password"),
            email="verify@test.com"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        session = create_session(db, test_user.id)

        # Verify token
        user = verify_session_token(db, session.token)

        assert user is not None
        assert user.id == test_user.id
        assert user.username == "verify_session_user"

        # Clean up
        db.delete(session)
        db.delete(test_user)
        db.commit()
    finally:
        db.close()


def test_verify_session_token_invalid():
    """Test verifying an invalid session token."""
    db = SessionLocal()
    try:
        user = verify_session_token(db, "invalid_token_123")
        assert user is None
    finally:
        db.close()


def test_verify_session_token_expired():
    """Test that expired session is deleted and returns None."""
    db = SessionLocal()
    try:
        # Create test user
        test_user = User(
            username="expired_session_user",
            password_hash=hash_password("password"),
            email="expired@test.com"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        # Create session that's already expired
        expired_session = Session(
            user_id=test_user.id,
            token=create_session_token(),
            expires_at=datetime.utcnow() - timedelta(days=1)  # Expired yesterday
        )
        db.add(expired_session)
        db.commit()
        session_id = expired_session.id
        token = expired_session.token

        # Try to verify expired token
        user = verify_session_token(db, token)

        # Should return None
        assert user is None

        # Session should be deleted
        deleted_session = db.query(Session).filter(Session.id == session_id).first()
        assert deleted_session is None

        # Clean up user
        db.delete(test_user)
        db.commit()
    finally:
        db.close()


def test_delete_session():
    """Test deleting a session."""
    db = SessionLocal()
    try:
        # Create test user and session
        test_user = User(
            username="delete_session_user",
            password_hash=hash_password("password"),
            email="delete@test.com"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        session = create_session(db, test_user.id)
        token = session.token
        session_id = session.id

        # Delete session
        result = delete_session(db, token)

        assert result is True

        # Verify session is gone
        deleted_session = db.query(Session).filter(Session.id == session_id).first()
        assert deleted_session is None

        # Clean up user
        db.delete(test_user)
        db.commit()
    finally:
        db.close()


def test_delete_session_not_found():
    """Test deleting a non-existent session returns False."""
    db = SessionLocal()
    try:
        result = delete_session(db, "non_existent_token")
        assert result is False
    finally:
        db.close()


def test_cleanup_expired_sessions():
    """Test cleanup of expired sessions."""
    db = SessionLocal()
    try:
        # Create test user
        test_user = User(
            username="cleanup_test_user",
            password_hash=hash_password("password"),
            email="cleanup@test.com"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        # Create 3 expired sessions
        for i in range(3):
            expired_session = Session(
                user_id=test_user.id,
                token=create_session_token(),
                expires_at=datetime.utcnow() - timedelta(days=i+1)
            )
            db.add(expired_session)

        # Create 2 valid sessions
        for i in range(2):
            valid_session = Session(
                user_id=test_user.id,
                token=create_session_token(),
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
            db.add(valid_session)

        db.commit()

        # Run cleanup
        deleted_count = cleanup_expired_sessions(db)

        # Should have deleted 3 expired sessions
        assert deleted_count == 3

        # Verify only 2 sessions remain
        remaining_sessions = db.query(Session).filter(
            Session.user_id == test_user.id
        ).all()
        assert len(remaining_sessions) == 2

        # Clean up
        db.delete(test_user)  # Cascade deletes remaining sessions
        db.commit()
    finally:
        db.close()


def test_cleanup_expired_sessions_none_expired():
    """Test cleanup when no sessions are expired."""
    db = SessionLocal()
    try:
        deleted_count = cleanup_expired_sessions(db)
        assert deleted_count == 0
    finally:
        db.close()
