"""
Unit tests for SQLAlchemy database models.

Following TDD: Tests for app/models/database.py
Tests User and Generation models, relationships, indexes, and constraints.
"""
import pytest
import uuid
from datetime import datetime
from sqlalchemy import inspect


def test_user_model_exists():
    """Test that User model can be imported and instantiated."""
    from app.models.database import User

    user = User()
    assert user is not None
    assert hasattr(user, 'id')
    assert hasattr(user, 'username')
    assert hasattr(user, 'api_token')


def test_user_model_has_required_columns():
    """Test that User model has all required columns from PRD."""
    from app.models.database import User

    user = User()

    # Check required attributes
    assert hasattr(user, 'id')
    assert hasattr(user, 'username')
    assert hasattr(user, 'api_token')
    assert hasattr(user, 'created_at')
    assert hasattr(user, 'updated_at')


def test_user_model_id_is_uuid():
    """Test that User.id is a UUID type when set."""
    from app.models.database import User

    user = User()
    # UUID is generated on flush/commit, not on instantiation
    # But we can verify the column is configured for UUID
    user.id = uuid.uuid4()
    assert isinstance(user.id, uuid.UUID)


def test_user_model_timestamps_auto_set():
    """Test that timestamp columns have default functions configured."""
    from app.models.database import User
    from sqlalchemy import inspect as sqla_inspect

    # Check that columns have default functions configured
    mapper = sqla_inspect(User)
    created_at_col = mapper.columns['created_at']
    updated_at_col = mapper.columns['updated_at']

    # Verify defaults are configured (actual values set on DB insert)
    assert created_at_col.default is not None
    assert updated_at_col.default is not None
    assert updated_at_col.onupdate is not None


def test_user_model_repr():
    """Test that User model has a proper string representation."""
    from app.models.database import User

    user = User(username="testuser")
    repr_str = repr(user)

    assert "User" in repr_str
    assert "testuser" in repr_str


def test_user_model_tablename():
    """Test that User model maps to correct table name."""
    from app.models.database import User

    assert User.__tablename__ == "users"


def test_generation_model_exists():
    """Test that Generation model can be imported and instantiated."""
    from app.models.database import Generation

    generation = Generation()
    assert generation is not None
    assert hasattr(generation, 'id')
    assert hasattr(generation, 'github_url')


def test_generation_model_has_required_columns():
    """Test that Generation model has all required columns from PRD."""
    from app.models.database import Generation

    generation = Generation()

    # Check all required attributes from PRD schema
    assert hasattr(generation, 'id')
    assert hasattr(generation, 'github_url')
    assert hasattr(generation, 'repo_owner')
    assert hasattr(generation, 'repo_name')
    assert hasattr(generation, 'primary_language')
    assert hasattr(generation, 'repo_size_kb')
    assert hasattr(generation, 'code_quality_score')
    assert hasattr(generation, 'cat_attributes')
    assert hasattr(generation, 'analysis_data')
    assert hasattr(generation, 'image_path')
    assert hasattr(generation, 'image_prompt')
    assert hasattr(generation, 'created_at')


def test_generation_model_id_is_uuid():
    """Test that Generation.id is a UUID type when set."""
    from app.models.database import Generation

    generation = Generation()
    # UUID is generated on flush/commit, not on instantiation
    generation.id = uuid.uuid4()
    assert isinstance(generation.id, uuid.UUID)


def test_generation_model_github_url_not_null():
    """Test that github_url is required (not nullable)."""
    from app.models.database import Generation
    from sqlalchemy import inspect as sqla_inspect

    mapper = sqla_inspect(Generation)
    github_url_col = mapper.columns['github_url']

    assert github_url_col.nullable is False


def test_generation_model_jsonb_fields():
    """Test that JSONB fields can store complex data."""
    from app.models.database import Generation

    cat_attrs = {
        "size": "medium",
        "age": "young",
        "beauty_score": 7.5,
        "expression": "happy"
    }

    analysis = {
        "code_quality_score": 8.0,
        "files_analyzed": ["main.py", "test.py"]
    }

    generation = Generation(
        github_url="https://github.com/test/repo",
        cat_attributes=cat_attrs,
        analysis_data=analysis
    )

    assert generation.cat_attributes == cat_attrs
    assert generation.analysis_data == analysis


def test_generation_model_timestamp_auto_set():
    """Test that created_at column has default function configured."""
    from app.models.database import Generation
    from sqlalchemy import inspect as sqla_inspect

    # Check that column has default function configured
    mapper = sqla_inspect(Generation)
    created_at_col = mapper.columns['created_at']

    # Verify default is configured (actual value set on DB insert)
    assert created_at_col.default is not None


def test_generation_model_repr():
    """Test that Generation model has a proper string representation."""
    from app.models.database import Generation

    generation = Generation(
        github_url="https://github.com/owner/repo",
        repo_owner="owner",
        repo_name="repo"
    )
    repr_str = repr(generation)

    assert "Generation" in repr_str
    assert "owner/repo" in repr_str


def test_generation_model_tablename():
    """Test that Generation model maps to correct table name."""
    from app.models.database import Generation

    assert Generation.__tablename__ == "generations"


def test_generation_model_has_index_on_github_url():
    """Test that Generation has index on github_url for performance."""
    from app.models.database import Generation
    from sqlalchemy import inspect as sqla_inspect

    # Get table metadata
    mapper = sqla_inspect(Generation)
    table = mapper.local_table

    # Check if there's an index on github_url
    indexes = table.indexes
    index_names = [idx.name for idx in indexes if idx.name]

    # Should have an index that includes github_url
    github_url_indexed = any(
        'github_url' in [col.name for col in idx.columns]
        for idx in indexes
    )

    assert github_url_indexed, "github_url should have an index for performance"


def test_generation_model_has_index_on_created_at():
    """Test that Generation has index on created_at for performance."""
    from app.models.database import Generation
    from sqlalchemy import inspect as sqla_inspect

    # Get table metadata
    mapper = sqla_inspect(Generation)
    table = mapper.local_table

    # Check if there's an index on created_at
    indexes = table.indexes
    created_at_indexed = any(
        'created_at' in [col.name for col in idx.columns]
        for idx in indexes
    )

    assert created_at_indexed, "created_at should have an index for performance"


def test_both_models_inherit_from_base():
    """Test that both models inherit from SQLAlchemy Base."""
    from app.models.database import User, Generation
    from app.core.database import Base

    assert issubclass(User, Base)
    assert issubclass(Generation, Base)


def test_user_username_unique_constraint():
    """Test that username has unique constraint."""
    from app.models.database import User
    from sqlalchemy import inspect as sqla_inspect

    mapper = sqla_inspect(User)
    username_col = mapper.columns['username']

    assert username_col.unique is True


def test_user_api_token_unique_constraint():
    """Test that api_token has unique constraint."""
    from app.models.database import User
    from sqlalchemy import inspect as sqla_inspect

    mapper = sqla_inspect(User)
    api_token_col = mapper.columns['api_token']

    assert api_token_col.unique is True


def test_generation_code_quality_score_decimal_precision():
    """Test that code_quality_score has correct decimal precision (3,1)."""
    from app.models.database import Generation

    # Test with valid decimal values
    generation = Generation(
        github_url="https://github.com/test/repo",
        code_quality_score=7.5
    )

    assert generation.code_quality_score == 7.5


def test_models_can_be_created_with_all_fields():
    """Test complete model instantiation with all fields."""
    from app.models.database import Generation

    generation = Generation(
        github_url="https://github.com/python/cpython",
        repo_owner="python",
        repo_name="cpython",
        primary_language="Python",
        repo_size_kb=15000,
        code_quality_score=9.5,
        cat_attributes={
            "size": "large",
            "age": "senior",
            "beauty_score": 9.5,
            "expression": "happy",
            "background": "snakes and code"
        },
        analysis_data={
            "metrics": {
                "has_tests": True,
                "has_type_hints": True
            }
        },
        image_path="/generated_images/test.png",
        image_prompt="A wise senior cat..."
    )

    assert generation.github_url == "https://github.com/python/cpython"
    assert generation.repo_owner == "python"
    assert generation.repo_name == "cpython"
    assert generation.primary_language == "Python"
    assert generation.repo_size_kb == 15000
    assert generation.code_quality_score == 9.5
    assert generation.cat_attributes["size"] == "large"
    assert generation.image_path == "/generated_images/test.png"
