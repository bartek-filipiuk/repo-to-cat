"""
Unit tests for database configuration and connection.

Tests database connection, session creation, and model operations.
"""
import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from datetime import datetime, timedelta

from app.core.database import engine, SessionLocal, get_db
from app.models.database import User, Generation, Session


def test_database_connection():
    """Test that database connection can be established."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            assert result.scalar() == 1
    except OperationalError as e:
        pytest.fail(f"Database connection failed: {e}")


def test_session_creation():
    """Test that database session can be created."""
    session = SessionLocal()
    assert session is not None
    session.close()


def test_get_db_dependency():
    """Test the get_db dependency function."""
    db_generator = get_db()
    db = next(db_generator)
    assert db is not None
    # Clean up
    try:
        next(db_generator)
    except StopIteration:
        pass  # Expected behavior


def test_user_table_exists():
    """Test that the users table exists in the database."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')")
        )
        assert result.scalar() is True


def test_generation_table_exists():
    """Test that the generations table exists in the database."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'generations')")
        )
        assert result.scalar() is True


def test_create_user():
    """Test creating a user in the database with authentication fields."""
    session = SessionLocal()
    try:
        # Create a test user with password_hash
        test_user = User(
            username="test_user",
            password_hash="hashed_password_123",
            email="test@example.com",
            api_token="test_token_123"
        )
        session.add(test_user)
        session.commit()
        session.refresh(test_user)

        # Verify user was created
        assert test_user.id is not None
        assert test_user.username == "test_user"
        assert test_user.password_hash == "hashed_password_123"
        assert test_user.email == "test@example.com"
        assert test_user.created_at is not None

        # Clean up
        session.delete(test_user)
        session.commit()
    finally:
        session.close()


def test_create_generation():
    """Test creating a generation record in the database."""
    session = SessionLocal()
    try:
        # Create a test generation
        test_gen = Generation(
            github_url="https://github.com/test/repo",
            repo_owner="test",
            repo_name="repo",
            primary_language="Python",
            repo_size_kb=1000,
            code_quality_score=8.5,
            cat_attributes={"size": "chonky", "color": "orange"},
            analysis_data={"score": 85},
            image_path="/path/to/image.png",
            image_prompt="A happy orange chonky cat"
        )
        session.add(test_gen)
        session.commit()
        session.refresh(test_gen)

        # Verify generation was created
        assert test_gen.id is not None
        assert test_gen.github_url == "https://github.com/test/repo"
        assert test_gen.code_quality_score == 8.5
        assert test_gen.cat_attributes == {"size": "chonky", "color": "orange"}

        # Clean up
        session.delete(test_gen)
        session.commit()
    finally:
        session.close()


def test_sessions_table_exists():
    """Test that the sessions table exists in the database."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sessions')")
        )
        assert result.scalar() is True


def test_create_session():
    """Test creating a session linked to a user."""
    session = SessionLocal()
    try:
        # Create a user first
        test_user = User(
            username="session_test_user",
            password_hash="hashed_password",
            email="session@example.com"
        )
        session.add(test_user)
        session.commit()
        session.refresh(test_user)

        # Create a session for the user
        test_session = Session(
            user_id=test_user.id,
            token="test_session_token_abc123",
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        session.add(test_session)
        session.commit()
        session.refresh(test_session)

        # Verify session was created
        assert test_session.id is not None
        assert test_session.user_id == test_user.id
        assert test_session.token == "test_session_token_abc123"
        assert test_session.expires_at > datetime.utcnow()
        assert test_session.created_at is not None

        # Verify relationship
        assert test_session.user.username == "session_test_user"

        # Clean up
        session.delete(test_session)
        session.delete(test_user)
        session.commit()
    finally:
        session.close()


def test_user_sessions_relationship():
    """Test that User.sessions relationship works."""
    session = SessionLocal()
    try:
        # Create user
        test_user = User(
            username="relationship_test_user",
            password_hash="hashed_password",
            email="relationship@example.com"
        )
        session.add(test_user)
        session.commit()
        session.refresh(test_user)

        # Create multiple sessions
        session1 = Session(
            user_id=test_user.id,
            token="token_1",
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        session2 = Session(
            user_id=test_user.id,
            token="token_2",
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        session.add(session1)
        session.add(session2)
        session.commit()

        # Refresh user to load relationship
        session.refresh(test_user)

        # Verify relationship
        assert len(test_user.sessions) == 2
        assert session1 in test_user.sessions
        assert session2 in test_user.sessions

        # Clean up
        session.delete(test_user)  # Should cascade delete sessions
        session.commit()
    finally:
        session.close()


def test_cascade_delete_sessions():
    """Test that deleting a user cascades to sessions."""
    session = SessionLocal()
    try:
        # Create user with session
        test_user = User(
            username="cascade_test_user",
            password_hash="hashed_password",
            email="cascade@example.com"
        )
        session.add(test_user)
        session.commit()
        session.refresh(test_user)

        test_session = Session(
            user_id=test_user.id,
            token="cascade_token",
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        session.add(test_session)
        session.commit()
        session_id = test_session.id

        # Delete user
        session.delete(test_user)
        session.commit()

        # Verify session was also deleted
        deleted_session = session.query(Session).filter(Session.id == session_id).first()
        assert deleted_session is None
    finally:
        session.close()


def test_generation_with_user_id():
    """Test creating a generation linked to a user."""
    session = SessionLocal()
    try:
        # Create user
        test_user = User(
            username="gen_test_user",
            password_hash="hashed_password",
            email="gen@example.com"
        )
        session.add(test_user)
        session.commit()
        session.refresh(test_user)

        # Create generation with user_id
        test_gen = Generation(
            github_url="https://github.com/test/repo",
            repo_owner="test",
            repo_name="repo",
            user_id=test_user.id
        )
        session.add(test_gen)
        session.commit()
        session.refresh(test_gen)

        # Verify relationship
        assert test_gen.user_id == test_user.id
        assert test_gen.user.username == "gen_test_user"
        assert test_gen in test_user.generations

        # Clean up
        session.delete(test_gen)
        session.delete(test_user)
        session.commit()
    finally:
        session.close()


def test_generation_without_user_id():
    """Test that generation can be created without user_id (nullable)."""
    session = SessionLocal()
    try:
        # Create generation without user_id
        test_gen = Generation(
            github_url="https://github.com/test/anonymous",
            repo_owner="test",
            repo_name="anonymous"
        )
        session.add(test_gen)
        session.commit()
        session.refresh(test_gen)

        # Verify it was created successfully
        assert test_gen.id is not None
        assert test_gen.user_id is None
        assert test_gen.user is None

        # Clean up
        session.delete(test_gen)
        session.commit()
    finally:
        session.close()
