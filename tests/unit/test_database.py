"""
Unit tests for database configuration and connection.

Tests database connection, session creation, and model operations.
"""
import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.core.database import engine, SessionLocal, get_db
from app.models.database import User, Generation


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
    """Test creating a user in the database."""
    session = SessionLocal()
    try:
        # Create a test user
        test_user = User(username="test_user", api_token="test_token_123")
        session.add(test_user)
        session.commit()
        session.refresh(test_user)

        # Verify user was created
        assert test_user.id is not None
        assert test_user.username == "test_user"
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
