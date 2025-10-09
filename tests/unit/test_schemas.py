"""
Unit tests for Pydantic API schemas.

Following TDD: Tests for app/api/schemas.py
Tests all request/response models matching PRD.md API specifications.
"""
import pytest
from pydantic import ValidationError
from datetime import datetime


def test_generate_request_schema_exists():
    """Test that GenerateRequest schema can be imported."""
    from app.api.schemas import GenerateRequest

    request = GenerateRequest(github_url="https://github.com/owner/repo")
    assert request is not None


def test_generate_request_requires_github_url():
    """Test that GenerateRequest requires github_url field."""
    from app.api.schemas import GenerateRequest

    # Should raise validation error without github_url
    with pytest.raises(ValidationError) as exc_info:
        GenerateRequest()

    assert "github_url" in str(exc_info.value)


def test_generate_request_validates_url_format():
    """Test that GenerateRequest validates URL format."""
    from app.api.schemas import GenerateRequest

    # Valid GitHub URLs
    valid_urls = [
        "https://github.com/owner/repo",
        "https://github.com/python/cpython",
        "https://github.com/owner-name/repo-name",
    ]

    for url in valid_urls:
        request = GenerateRequest(github_url=url)
        assert request.github_url == url


def test_generate_request_rejects_invalid_urls():
    """Test that GenerateRequest rejects non-GitHub URLs."""
    from app.api.schemas import GenerateRequest

    invalid_urls = [
        "not-a-url",
        "http://example.com",
        "https://gitlab.com/owner/repo",
        "",
    ]

    for url in invalid_urls:
        with pytest.raises(ValidationError):
            GenerateRequest(github_url=url)


def test_repository_info_schema_exists():
    """Test that RepositoryInfo schema exists with required fields."""
    from app.api.schemas import RepositoryInfo

    repo_info = RepositoryInfo(
        url="https://github.com/owner/repo",
        name="repo",
        owner="owner",
        primary_language="Python",
        size_kb=1234,
        stars=567
    )

    assert repo_info.url == "https://github.com/owner/repo"
    assert repo_info.name == "repo"
    assert repo_info.owner == "owner"
    assert repo_info.primary_language == "Python"
    assert repo_info.size_kb == 1234
    assert repo_info.stars == 567


def test_repository_info_stars_optional():
    """Test that stars field is optional in RepositoryInfo."""
    from app.api.schemas import RepositoryInfo

    # Stars should be optional (can be None)
    repo_info = RepositoryInfo(
        url="https://github.com/owner/repo",
        name="repo",
        owner="owner",
        primary_language="Python",
        size_kb=1234
    )

    assert repo_info.stars is None or isinstance(repo_info.stars, int)


def test_analysis_result_schema_exists():
    """Test that AnalysisResult schema exists with required fields."""
    from app.api.schemas import AnalysisResult

    analysis = AnalysisResult(
        code_quality_score=7.5,
        files_analyzed=["README.md", "main.py"],
        metrics={
            "line_length_avg": 85,
            "has_tests": True
        }
    )

    assert analysis.code_quality_score == 7.5
    assert len(analysis.files_analyzed) == 2
    assert analysis.metrics["has_tests"] is True


def test_analysis_result_score_range_validation():
    """Test that code_quality_score is validated to be 0-10."""
    from app.api.schemas import AnalysisResult

    # Valid scores
    valid_scores = [0.0, 5.5, 10.0]
    for score in valid_scores:
        analysis = AnalysisResult(
            code_quality_score=score,
            files_analyzed=["test.py"],
            metrics={}
        )
        assert analysis.code_quality_score == score

    # Invalid scores
    invalid_scores = [-1.0, 11.0, 15.5]
    for score in invalid_scores:
        with pytest.raises(ValidationError):
            AnalysisResult(
                code_quality_score=score,
                files_analyzed=["test.py"],
                metrics={}
            )


def test_cat_attributes_schema_exists():
    """Test that CatAttributes schema exists with required fields."""
    from app.api.schemas import CatAttributes

    cat_attrs = CatAttributes(
        size="medium",
        age="young",
        beauty_score=7.5,
        expression="happy",
        background="snakes and code"
    )

    assert cat_attrs.size == "medium"
    assert cat_attrs.age == "young"
    assert cat_attrs.beauty_score == 7.5
    assert cat_attrs.expression == "happy"
    assert cat_attrs.background == "snakes and code"


def test_cat_attributes_accessories_optional():
    """Test that accessories field is optional."""
    from app.api.schemas import CatAttributes

    # Without accessories
    cat_attrs = CatAttributes(
        size="medium",
        age="young",
        beauty_score=7.5,
        expression="happy",
        background="snakes"
    )

    assert cat_attrs.accessories is None or isinstance(cat_attrs.accessories, list)


def test_cat_attributes_with_accessories():
    """Test CatAttributes with accessories list."""
    from app.api.schemas import CatAttributes

    cat_attrs = CatAttributes(
        size="medium",
        age="young",
        beauty_score=7.5,
        expression="happy",
        background="snakes",
        accessories=["bow tie", "collar"]
    )

    assert cat_attrs.accessories == ["bow tie", "collar"]


def test_image_data_schema_exists():
    """Test that ImageData schema exists with required fields."""
    from app.api.schemas import ImageData

    image_data = ImageData(
        url="/generated_images/test.png",
        binary="base64data",
        prompt="A beautiful cat..."
    )

    assert image_data.url == "/generated_images/test.png"
    assert image_data.binary == "base64data"
    assert image_data.prompt == "A beautiful cat..."


def test_generate_response_schema_exists():
    """Test that GenerateResponse schema exists with all nested schemas."""
    from app.api.schemas import (
        GenerateResponse, RepositoryInfo, AnalysisResult,
        CatAttributes, ImageData
    )

    response = GenerateResponse(
        success=True,
        generation_id="uuid-here",
        repository=RepositoryInfo(
            url="https://github.com/owner/repo",
            name="repo",
            owner="owner",
            primary_language="Python",
            size_kb=1234,
            stars=567
        ),
        analysis=AnalysisResult(
            code_quality_score=7.5,
            files_analyzed=["main.py"],
            metrics={"has_tests": True}
        ),
        cat_attributes=CatAttributes(
            size="medium",
            age="young",
            beauty_score=7.5,
            expression="happy",
            background="snakes"
        ),
        image=ImageData(
            url="/generated_images/test.png",
            binary="base64",
            prompt="A cat"
        ),
        timestamp=datetime.utcnow()
    )

    assert response.success is True
    assert response.generation_id == "uuid-here"
    assert response.repository.name == "repo"
    assert response.analysis.code_quality_score == 7.5
    assert response.cat_attributes.size == "medium"
    assert response.image.url == "/generated_images/test.png"


def test_generate_response_matches_prd_structure():
    """Test that GenerateResponse matches exact structure from PRD.md."""
    from app.api.schemas import GenerateResponse

    # Create response matching PRD example
    response_dict = {
        "success": True,
        "generation_id": "uuid-here",
        "repository": {
            "url": "https://github.com/owner/repo",
            "name": "repo",
            "owner": "owner",
            "primary_language": "Python",
            "size_kb": 1234,
            "stars": 567
        },
        "analysis": {
            "code_quality_score": 7.5,
            "files_analyzed": ["README.md", "src/main.py"],
            "metrics": {
                "line_length_avg": 85,
                "function_length_avg": 25,
                "has_tests": True,
                "has_type_hints": True,
                "has_documentation": True
            }
        },
        "cat_attributes": {
            "size": "medium",
            "age": "young",
            "beauty_score": 7.5,
            "expression": "happy",
            "background": "snakes and code",
            "accessories": ["bow tie", "collar"]
        },
        "image": {
            "url": "/generated_images/uuid-here.png",
            "binary": "base64-encoded-image-data",
            "prompt": "A young, beautiful medium-sized cat..."
        },
        "timestamp": "2025-10-07T12:34:56Z"
    }

    response = GenerateResponse(**response_dict)
    assert response.success is True
    assert len(response.analysis.files_analyzed) == 2


def test_health_check_response_schema_exists():
    """Test that HealthCheckResponse schema exists."""
    from app.api.schemas import HealthCheckResponse

    health = HealthCheckResponse(
        status="healthy",
        database={"status": "up"},
        timestamp=datetime.utcnow()
    )

    assert health.status == "healthy"
    assert health.database["status"] == "up"


def test_health_check_response_with_services():
    """Test HealthCheckResponse with full service status."""
    from app.api.schemas import HealthCheckResponse

    health = HealthCheckResponse(
        status="healthy",
        database={"status": "up"},
        services={
            "github_api": {"status": "up", "response_time_ms": 145},
            "openrouter": {"status": "up", "response_time_ms": 320}
        },
        timestamp=datetime.utcnow()
    )

    assert health.services["github_api"]["status"] == "up"
    assert health.services["openrouter"]["response_time_ms"] == 320


def test_schemas_are_json_serializable():
    """Test that all schemas can be converted to JSON."""
    from app.api.schemas import (
        GenerateRequest, GenerateResponse, RepositoryInfo,
        AnalysisResult, CatAttributes, ImageData
    )

    request = GenerateRequest(github_url="https://github.com/owner/repo")
    request_json = request.model_dump()
    assert "github_url" in request_json

    response = GenerateResponse(
        success=True,
        generation_id="test",
        repository=RepositoryInfo(
            url="https://github.com/owner/repo",
            name="repo",
            owner="owner",
            primary_language="Python",
            size_kb=100
        ),
        analysis=AnalysisResult(
            code_quality_score=5.0,
            files_analyzed=[],
            metrics={}
        ),
        cat_attributes=CatAttributes(
            size="small",
            age="kitten",
            beauty_score=5.0,
            expression="happy",
            background="code"
        ),
        image=ImageData(
            url="/test.png",
            binary="data",
            prompt="test"
        ),
        timestamp=datetime.utcnow()
    )

    response_json = response.model_dump()
    assert response_json["success"] is True


def test_schemas_have_config_for_json_mode():
    """Test that schemas are configured for JSON compatibility."""
    from app.api.schemas import GenerateResponse

    # Should have json_schema_extra or model_config for API docs
    assert hasattr(GenerateResponse, 'model_config') or hasattr(GenerateResponse, 'Config')


def test_cat_attributes_size_values():
    """Test that cat size accepts expected values."""
    from app.api.schemas import CatAttributes

    valid_sizes = ["kitten", "small", "medium", "large", "chonky"]

    for size in valid_sizes:
        cat = CatAttributes(
            size=size,
            age="young",
            beauty_score=5.0,
            expression="happy",
            background="test"
        )
        assert cat.size == size


def test_cat_attributes_expression_values():
    """Test that cat expression accepts expected values."""
    from app.api.schemas import CatAttributes

    valid_expressions = ["happy", "neutral", "grumpy", "concerned"]

    for expression in valid_expressions:
        cat = CatAttributes(
            size="medium",
            age="young",
            beauty_score=5.0,
            expression=expression,
            background="test"
        )
        assert cat.expression == expression
